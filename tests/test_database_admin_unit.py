import pytest
from flask import Flask, g
from histarchexplorer.database.admin import (
    sanitize_richtext, get_config_links, get_config_properties,
    get_config_class_by_id, add_new_map, update_sort_order,
    get_licenses, get_file_licenses,
    get_all_logos_from_db, get_all_assets_from_db, get_openatlas_entity)
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
        # Just ensure it doesn't crash for now
        update_sort_order('tng.entities', [{'id': 1, 'order': 1}])

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
