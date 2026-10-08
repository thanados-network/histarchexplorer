import json
import logging
import re
from pathlib import Path
from unittest.mock import Mock

import psycopg2.extras
import pytest
from flask import g
from pydantic import ValidationError

from histarchexplorer import app, connect
from histarchexplorer.models.settings import (
    Settings, parse_vocabulary_ids, validate_vocabulary_filters)

SETTINGS_MODULE = 'histarchexplorer.models.settings'


@pytest.mark.parametrize('title', ['', 'Gräber & Funde'])
def test_vocabulary_title_persists(stored_settings, title):
    settings = Settings(vocabulary_title=title)
    settings.save_to_db()
    assert stored_settings['vocabulary_title'] == title
    assert Settings.load_from_db().vocabulary_title == title


def test_vocabulary_title_default():
    assert Settings().vocabulary_title == ''


@pytest.mark.parametrize(('value', 'expected'), [
    ('', []), (' \t\n', []), ('1', [1]),
    (' 2, 1, 2, 003 ', [2, 1, 3])])
def test_parse_vocabulary_ids(value, expected):
    assert parse_vocabulary_ids(value) == expected


@pytest.mark.parametrize('value', [
    ',', '1,', ',1', '1,,2', '1, ,2', '0', '-1', '+1', '1.0',
    '1e2', '١', '１', '1 2', 'abc', None, 1, [1]])
def test_parse_vocabulary_ids_rejects_invalid(value):
    with pytest.raises(ValueError):
        parse_vocabulary_ids(value)


@pytest.mark.parametrize(('include', 'exclude', 'expected'), [
    ([], [], ([], [])), ([2, 1, 2], [], ([2, 1], [])),
    ([], [3, 2, 3], ([], [3, 2]))])
def test_validate_vocabulary_filters(include, exclude, expected):
    assert validate_vocabulary_filters(include, exclude) == expected


INVALID_FILTERS = [
    ([1], [2]), ([0], []), ([-1], []), ([True], []),
    ([1.0], []), (['1'], []), ('1', []), (None, []),
    ((1,), []), ({1}, []), ([], [False]), ([], ['2']), ([1], ['2'])]


@pytest.mark.parametrize(('include', 'exclude'), INVALID_FILTERS)
def test_vocabulary_filters_reject_invalid(include, exclude):
    with pytest.raises(ValueError):
        validate_vocabulary_filters(include, exclude)
    with pytest.raises(ValidationError):
        Settings(
            vocabulary_include_ids=include,
            vocabulary_exclude_ids=exclude)


def test_vocabulary_defaults_and_menu():
    settings = Settings()
    assert settings.vocabulary_include_ids == []
    assert settings.vocabulary_exclude_ids == []
    assert settings.menu_management['vocabulary'] == {
        'show': True, 'page_type': 'default'}
    settings.vocabulary_include_ids.append(1)
    assert Settings().vocabulary_include_ids == []


def test_vocabulary_construction_normalizes_filters_and_menu():
    settings = Settings(
        vocabulary_include_ids=[3, 1, 3],
        menu_management={
            'about': {'show': False, 'page_type': 'custom'},
            'vocabulary': {
                'show': False, 'page_type': 'custom', 'label': 'Terms'}})
    assert settings.vocabulary_include_ids == [3, 1]
    assert settings.menu_management['about'] == {
        'show': False, 'page_type': 'custom'}
    assert settings.menu_management['vocabulary'] == {
        'show': False, 'page_type': 'default', 'label': 'Terms'}


@pytest.fixture()
def stored_settings(monkeypatch):
    stored = {}
    monkeypatch.setattr(
        'histarchexplorer.models.settings.create_settings_table', Mock())
    monkeypatch.setattr(
        'histarchexplorer.models.settings.get_settings',
        lambda: [{'key': key, 'value': value}
                 for key, value in stored.items()])
    monkeypatch.setattr(
        'histarchexplorer.models.settings.save_settings',
        lambda key, value: stored.update({key: value}))
    return stored


@pytest.mark.parametrize(('include', 'exclude'), INVALID_FILTERS)
def test_corrupt_stored_filters_fall_back_and_warn(
        stored_settings, caplog, include, exclude):
    stored_settings.update({
        'vocabulary_include_ids': include,
        'vocabulary_exclude_ids': exclude,
        'shown_types': 1234})
    with caplog.at_level(logging.WARNING, logger=SETTINGS_MODULE):
        settings = Settings.load_from_db()
    assert settings.vocabulary_include_ids == []
    assert settings.vocabulary_exclude_ids == []
    assert stored_settings['vocabulary_include_ids'] == []
    assert stored_settings['vocabulary_exclude_ids'] == []
    assert settings.shown_types == [1234]
    assert any(
        record.name == SETTINGS_MODULE
        and record.levelno == logging.WARNING
        and 'vocabulary' in record.message.lower()
        for record in caplog.records)


@pytest.mark.parametrize('as_json', [False, True])
def test_load_merges_menu_without_overwriting(stored_settings, as_json):
    menu = {'about': {'show': False, 'page_type': 'custom'}}
    stored_settings['menu_management'] = (
        json.dumps(menu) if as_json else menu)
    settings = Settings.load_from_db()
    assert settings.menu_management['about'] == menu['about']
    assert settings.menu_management['vocabulary'] == {
        'show': True, 'page_type': 'default'}
    assert settings.menu_management['search']['show'] is True


def test_load_keeps_vocabulary_visibility(stored_settings):
    stored_settings['menu_management'] = {
        'vocabulary': {'show': False, 'page_type': 'custom'}}
    settings = Settings.load_from_db()
    assert settings.menu_management['vocabulary'] == {
        'show': False, 'page_type': 'default'}


@pytest.mark.parametrize(('include', 'exclude'), INVALID_FILTERS)
def test_save_rejects_invalid_filters_before_any_write(
        monkeypatch, include, exclude):
    save = Mock()
    monkeypatch.setattr('histarchexplorer.models.settings.save_settings', save)
    settings = Settings()
    settings.vocabulary_include_ids = include
    settings.vocabulary_exclude_ids = exclude
    with pytest.raises(ValueError):
        settings.save_to_db()
    save.assert_not_called()


def test_save_normalizes_mutated_filters(stored_settings):
    settings = Settings()
    settings.vocabulary_exclude_ids.extend([2, 1, 2])
    settings.save_to_db()
    assert stored_settings['vocabulary_exclude_ids'] == [2, 1]


@pytest.mark.parametrize('page_type', ['default', 'individual'])
def test_vocabulary_page_type_persists(stored_settings, page_type):
    settings = Settings(menu_management={
        'vocabulary': {'show': False, 'page_type': page_type}})
    settings.save_to_db()
    loaded = Settings.load_from_db()
    assert loaded.menu_management['vocabulary'] == {
        'show': False, 'page_type': page_type}


@pytest.fixture()
def settings_cursor():
    with app.app_context():
        g.db = connect(app.config['DATABASE_NAME'])
        g.cursor = g.db.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield g.cursor
        finally:
            g.db.rollback()
            g.cursor.close()
            g.db.close()


@pytest.mark.parametrize('field', [
    'vocabulary_include_ids', 'vocabulary_exclude_ids'])
def test_vocabulary_filters_persist_and_reload(settings_cursor, field):
    settings = Settings(**{field: [3, 1, 3]})
    settings.save_to_db()
    settings_cursor.execute(
        'SELECT value FROM tng.system_settings WHERE key = %s', (field,))
    row = settings_cursor.fetchone()
    assert row is not None
    assert row['value'] == [3, 1]
    loaded = Settings.load_from_db()
    assert getattr(loaded, field) == [3, 1]
    other = ('vocabulary_exclude_ids' if field == 'vocabulary_include_ids'
             else 'vocabulary_include_ids')
    assert getattr(loaded, other) == []


UPGRADE_PATH = (
    Path(__file__).resolve().parents[1] / 'install/upgrade/0.6.0.sql')


def test_vocabulary_upgrade_has_no_transaction_commands():
    sql = UPGRADE_PATH.read_text()
    assert not re.search(r'\b(BEGIN|COMMIT|ROLLBACK)\b', sql, re.IGNORECASE)


@pytest.mark.parametrize(('vocabulary', 'present'), [
    (None, False), (None, True),
    ({'show': False, 'page_type': 'custom'}, True), (False, True)])
@pytest.mark.parametrize('field', [
    'vocabulary_include_ids', 'vocabulary_exclude_ids'])
def test_vocabulary_upgrade_preserves_existing_values(
        settings_cursor, vocabulary, present, field):
    menu: dict = {'about': {'show': False, 'page_type': 'custom'}}
    if present:
        menu['vocabulary'] = vocabulary
    settings_cursor.execute(
        'DELETE FROM tng.system_settings WHERE key IN (%s, %s, %s)',
        ('vocabulary_include_ids', 'vocabulary_exclude_ids',
         'menu_management'))
    settings_cursor.execute(
        'INSERT INTO tng.system_settings (key, value) VALUES (%s, %s)',
        ('menu_management', psycopg2.extras.Json(menu)))
    settings_cursor.execute(
        'INSERT INTO tng.system_settings (key, value) VALUES (%s, %s)',
        (field, psycopg2.extras.Json([7])))
    sql = UPGRADE_PATH.read_text()
    settings_cursor.execute(sql)
    settings_cursor.execute(sql)
    settings_cursor.execute('SELECT key, value FROM tng.system_settings')
    stored = {row['key']: row['value']
              for row in settings_cursor.fetchall()}
    assert stored[field] == [7]
    other = ('vocabulary_exclude_ids' if field == 'vocabulary_include_ids'
             else 'vocabulary_include_ids')
    assert stored[other] == []
    assert stored['menu_management']['about'] == menu['about']
    expected = (vocabulary if present else
                {'show': True, 'page_type': 'default'})
    assert stored['menu_management']['vocabulary'] == expected


def test_vocabulary_upgrade_inserts_missing_settings(settings_cursor):
    settings_cursor.execute(
        'DELETE FROM tng.system_settings WHERE key IN (%s, %s, %s, %s)',
        ('vocabulary_include_ids', 'vocabulary_exclude_ids',
         'menu_management', 'vocabulary_title'))
    settings_cursor.execute(UPGRADE_PATH.read_text())
    settings_cursor.execute('SELECT key, value FROM tng.system_settings')
    stored = {row['key']: row['value']
              for row in settings_cursor.fetchall()}
    assert stored['vocabulary_include_ids'] == []
    assert stored['vocabulary_exclude_ids'] == []
    assert stored['vocabulary_title'] == ''
    assert stored['menu_management'] == {
        'vocabulary': {'show': True, 'page_type': 'default'}}


def test_vocabulary_upgrade_preserves_title(settings_cursor):
    settings_cursor.execute(
        'DELETE FROM tng.system_settings WHERE key = %s',
        ('vocabulary_title',))
    settings_cursor.execute(
        'INSERT INTO tng.system_settings (key, value) VALUES (%s, %s)',
        ('vocabulary_title', psycopg2.extras.Json('Custom title')))
    settings_cursor.execute(UPGRADE_PATH.read_text())
    settings_cursor.execute(UPGRADE_PATH.read_text())
    settings_cursor.execute(
        'SELECT value FROM tng.system_settings WHERE key = %s',
        ('vocabulary_title',))
    assert settings_cursor.fetchone()['value'] == 'Custom title'
