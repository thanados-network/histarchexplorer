from unittest.mock import patch
import pytest
from flask.testing import FlaskClient
from histarchexplorer import app

def test_admin_index(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/admin/')
    assert rv.status_code == 200

def test_admin_tabs(authenticated_client: FlaskClient) -> None:
    tabs = [
        'sidebar-general', 'sidebar-colors', 'sidebar-menu-management',
        'sidebar-type-divisions', 'sidebar-case-studies', 'sidebar-class-visibility',
        'sidebar-logo-management', 'sidebar-team-management', 'sidebar-publications',
        'sidebar-licenses', 'sidebar-assets', 'sidebar-system'
    ]
    for tab in tabs:
        rv = authenticated_client.get(f'/admin/{tab}')
        assert rv.status_code == 200

def test_update_legal_notice(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.post('/admin/update_legal_notice', data={
        'legal_notice_de': 'German notice',
        'legal_notice_en': 'English notice'
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_add_delete_color(authenticated_client: FlaskClient) -> None:
    # Add color
    rv = authenticated_client.post('/admin/add_available_color', data={
        'new_color': '#aabbcc'
    }, follow_redirects=True)
    assert rv.status_code == 200
    
    # Delete color
    rv = authenticated_client.post('/admin/delete_available_color', data={
        'color_to_delete': '#aabbcc'
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_update_menu_management(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.post('/admin/update_menu_management', data={
        'show_about': 'on',
        'page_type_about': 'default'
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_update_general_settings(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.post('/admin/update_general_settings', data={
        'site_title': 'New Title',
        'contact_email': 'test@example.com',
        'case_study_id': '0'
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_update_type_divisions(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.post('/admin/update_type_divisions', data={
        'label_1': 'Test Division',
        'ids_1': '1,2,3',
        'icon_type_1': 'bootstrap',
        'icon_value_1': 'bi-box'
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_update_class_visibility(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.post('/admin/update_class_visibility', data={
        'shown_classes': ['Site', 'Person'],
        'hidden_classes': ['Reference']
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_clear_cache(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/admin/clear_cache', follow_redirects=True)
    assert rv.status_code == 200

def test_refresh_system_cache(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/admin/refresh_system_cache', follow_redirects=True)
    assert rv.status_code == 200

def test_logo_management(authenticated_client: FlaskClient) -> None:
    # Use existing routes from grep output
    rv = authenticated_client.post('/admin/upload_logo', data={
        'logo_name': 'Test Logo'
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_team_management(authenticated_client: FlaskClient) -> None:
    # Use add_entry for team/publications
    rv = authenticated_client.post('/admin/add_entry', data={
        'name': 'New Member',
        'class_id': '2' # person
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_license_management(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.post('/admin/add_license', data={
        'name': 'CC-BY',
        'url': 'http://example.com',
        'spdx_id': 'CC-BY-4.0',
        'uri': 'http://example.com/uri',
        'label': 'CC BY 4.0',
        'category': 'LICENSE'
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_admin_misc_routes(authenticated_client: FlaskClient) -> None:
    # Test backup_db
    rv = authenticated_client.get('/admin/backup_db')
    assert rv.status_code == 200
    
    # Test choose_index_background
    rv = authenticated_client.post('/admin/choose_index_background', data={
        'index_img': 'test.png',
        'mapselection': '1',
        'imgmap': 'map'
    }, follow_redirects=True)
    assert rv.status_code == 200
    
    # Test check_case_study_id_ajax
    rv = authenticated_client.get('/admin/check_case_study_id_ajax/8240')
    assert rv.status_code == 200

def test_delete_entry(authenticated_client: FlaskClient) -> None:
    # We use a valid tab name from admin.py match/case
    rv = authenticated_client.get('/admin/delete_entry/1/sidebar-team', follow_redirects=True)
    assert rv.status_code == 200

def test_admin_additional_routes(authenticated_client: FlaskClient) -> None:
    # Test set_main_logo
    rv = authenticated_client.post('/admin/set_main_logo', data={
        'main_logo': 'test.png'
    }, follow_redirects=True)
    assert rv.status_code == 200
    
    # Test update_footer_content
    rv = authenticated_client.post('/admin/update_footer_content', data={
        'footer_logos': ['1', '2']
    }, follow_redirects=True)
    assert rv.status_code == 200
    
    # Test rename_logo
    rv = authenticated_client.post('/admin/rename_logo', data={
        'old_name': 'old.png',
        'new_name': 'new.png'
    }, follow_redirects=True)
    assert rv.status_code == 200

import io

def test_admin_file_uploads(authenticated_client: FlaskClient) -> None:
    # Test upload_logo
    data = {
        'logo_file': (io.BytesIO(b"fake image data"), 'test.png'),
        'logo_name': 'Test Logo'
    }
    rv = authenticated_client.post('/admin/upload_logo', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert rv.status_code == 200

    # Test upload_asset
    data = {
        'asset_file': (io.BytesIO(b"fake asset data"), 'test.txt'),
    }
    rv = authenticated_client.post('/admin/upload_asset', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert rv.status_code == 200

    # Test upload_file
    data = {
        'file': (io.BytesIO(b"fake data"), 'test.dat'),
        'file_type': 'team'
    }
    rv = authenticated_client.post('/admin/upload_file', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert rv.status_code == 200

def test_admin_map_management(authenticated_client: FlaskClient) -> None:
    # Test add_map
    rv = authenticated_client.post('/admin/add_map', data={
        'name': 'Test Map',
        'url': 'http://tile.example.com/{z}/{x}/{y}.png'
    }, follow_redirects=True)
    assert rv.status_code == 200
    
    # Test edit_map
    rv = authenticated_client.post('/admin/edit_map', data={
        'id': '1',
        'name': 'Updated Map',
        'url': 'http://tile.example.com/{z}/{x}/{y}.png'
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_admin_cache_and_colors(authenticated_client: FlaskClient) -> None:
    # Test update_entity_colors
    rv = authenticated_client.post('/admin/update_entity_colors', data={
        'entity_colors-places': '#123456'
    }, follow_redirects=True)
    assert rv.status_code == 200
    
    # Test refresh_entity_cache
    # Mock trigger_cache_warmup to avoid starting subprocesses
    with patch('histarchexplorer.views.admin.trigger_cache_warmup') as mock_trigger:
        rv = authenticated_client.get('/admin/refresh-entity-cache', follow_redirects=True)
        assert rv.status_code == 200
        assert mock_trigger.called

def test_edit_entry(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.post('/edit_entry', data={
        'id': '1',
        'name': 'Updated Name'
    }, follow_redirects=True)
    assert rv.status_code == 200
