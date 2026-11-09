import pytest
from flask import Flask, g
from histarchexplorer.database.admin import (
    sanitize_richtext, get_config_links, get_config_properties,
    get_config_class_by_id, add_new_map, update_sort_order,
    get_licenses, get_file_licenses,
    get_all_logos_from_db, get_all_assets_from_db, get_openatlas_entity)
from histarchexplorer.database.admin import update_predefined_filter_order
from histarchexplorer.models.config import get_config_classes
from histarchexplorer import get_sidebar_icons, get_type_divisions
from unittest.mock import MagicMock, patch

def test_sanitize_richtext():
    html = '<p>Test <script>alert(1)</script> <b>Bold</b></p>'
    sanitized = sanitize_richtext(html)
    assert '<script>' not in sanitized
    assert '<b>Bold</b>' in sanitized

def test_get_config_links(app_instance):
    with app_instance.test_request_context():
        g.cursor = MagicMock()
        g.cursor.fetchall.return_value = [{'link_id': 1}]
        assert get_config_links() == [{'link_id': 1}]

def test_get_config_properties(app_instance):
    with app_instance.test_request_context():
        g.cursor = MagicMock()
        g.cursor.fetchall.return_value = [{'id': 1}]
        assert get_config_properties() == [{'id': 1}]

def test_get_config_class_by_id(app_instance):
    with app_instance.test_request_context():
        g.cursor = MagicMock()
        g.cursor.fetchone.return_value = {'class_id': 5}
        assert get_config_class_by_id(1) == 5
        
        g.cursor.fetchone.return_value = None
        assert get_config_class_by_id(1) is None

def test_add_new_map(app_instance):
    with app_instance.test_request_context():
        g.cursor = MagicMock()
        g.cursor.fetchone.return_value = {'id': 10}
        data = {'name': 'n', 'display_name': 'd', 'sort_order': 1, 'tile_string': 't'}
        assert add_new_map(data) == 10
        
        g.cursor.fetchone.return_value = None
        assert add_new_map(data) == 0

def test_update_sort_order(app_instance):
    with app_instance.test_request_context():
        g.cursor = MagicMock()
        update_sort_order('tng.entities', [{'id': 1, 'order': 1}])
        with pytest.raises(ValueError, match='Invalid table for sort order'):
            update_sort_order('tng.users', [{'id': 1, 'order': 1}])


def test_update_file_license_zero_clears_or_uses_null(app_instance):
    from histarchexplorer.database.admin import update_file_license
    with app_instance.test_request_context():
        g.cursor = MagicMock()
        g.cursor.fetchone.return_value = {'id': 42}
        # license_id=0 and empty attribution -> deletes license entry
        update_file_license('logo.png', 0, '')
        assert any(
            'DELETE FROM tng.file_licenses' in str(call.args[0])
            for call in g.cursor.execute.call_args_list)

        g.cursor.reset_mock()
        g.cursor.fetchone.return_value = {'id': 42}
        # license_id=0 with attribution -> inserts None for license_id
        update_file_license('logo.png', 0, 'CC Author')
        last_args = g.cursor.execute.call_args[0][1]
        assert last_args['license_id'] is None
        assert last_args['attribution'] == 'CC Author'


def test_fetch_doi_metadata_rejects_invalid_doi():
    from histarchexplorer.utils.doi import fetch_doi_metadata
    assert fetch_doi_metadata('../../etc/passwd') is None
    assert fetch_doi_metadata('10.1000/../secret') is None
    assert fetch_doi_metadata('not-a-doi') is None


def test_load_or_generate_secret_key(tmp_path):
    from histarchexplorer import _load_or_generate_secret_key
    dummy_app = Flask(__name__, instance_path=str(tmp_path))
    dummy_app.config['SECRET_KEY'] = 'CHANGE ME'

    generated = _load_or_generate_secret_key(dummy_app)
    assert len(generated) == 64
    key_file = tmp_path / '.secret_key'
    assert key_file.exists()
    assert (key_file.stat().st_mode & 0o777) == 0o600
    assert _load_or_generate_secret_key(dummy_app) == generated

def test_get_licenses(app_instance):
    with app_instance.test_request_context():
        g.cursor = MagicMock()
        g.cursor.fetchall.return_value = [{'id': 1}]
        assert get_licenses() == [{'id': 1}]

def test_get_all_files(app_instance):
    with app_instance.test_request_context():
        g.cursor = MagicMock()
        g.cursor.fetchall.return_value = [{'id': 1, 'filename': 'F', 'is_default': False}]
        assert get_all_logos_from_db() == [{'id': 1, 'filename': 'F', 'is_default': False}]
        assert get_all_assets_from_db() == [{'id': 1, 'filename': 'F', 'is_default': False}]

def test_get_sidebar_icons(app_instance):
    with app_instance.test_request_context():
        app_instance.config['SIDEBAR_ICONS'] = {'images': {}, 'css_icon_class': {}}
        res = get_sidebar_icons()
        assert isinstance(res, dict)

def test_get_type_divisions(app_instance):
    with app_instance.test_request_context():
        g.settings = MagicMock()
        g.settings.type_divisions = {}
        res = get_type_divisions()
        assert isinstance(res, dict)

def test_get_config_classes(app_instance):
    with app_instance.test_request_context():
        g.cursor = MagicMock()
        g.cursor.fetchall.return_value = [{'id': 1, 'name': 'N'}]
        assert get_config_classes() == {'N': 1}

def test_get_openatlas_entity(app_instance):
    with app_instance.test_request_context():
        g.openatlas_cursor = MagicMock()
        g.openatlas_cursor.fetchone.return_value = {'id': 1}
        assert get_openatlas_entity(1) == {'id': 1}


def test_update_predefined_filter_order_uses_two_phase_update(app_instance):
    with app_instance.test_request_context():
        g.cursor = MagicMock()
        g.cursor.fetchone.return_value = {'max_sortorder': 2}
        params = [{'id': 1, 'order': 2}, {'id': 2, 'order': 1}]

        update_predefined_filter_order(params)

        g.cursor.execute.assert_called_once_with(
            'SELECT COALESCE(MAX(sortorder), 0) AS max_sortorder '
            'FROM tng.predefined_filters')
        assert g.cursor.executemany.call_count == 2

        first_sql, first_params = g.cursor.executemany.call_args_list[0][0]
        assert first_sql == (
            'UPDATE tng.predefined_filters SET sortorder = %(temp_order)s '
            'WHERE id = %(id)s')
        assert first_params == [
            {'temp_order': 7, 'id': 1},
            {'temp_order': 6, 'id': 2}]

        second_sql, second_params = g.cursor.executemany.call_args_list[1][0]
        assert second_sql == (
            'UPDATE tng.predefined_filters SET sortorder = %(order)s '
            'WHERE id = %(id)s')
        assert second_params == params
