import pytest
from flask.testing import FlaskClient
from unittest.mock import patch, MagicMock
import io

def test_admin_additional_routes(authenticated_client: FlaskClient):
    # Add a license first using the route
    authenticated_client.post('/admin/add_license', data={
        'spdx_id': 'CC-BY-4.0', 'uri': 'http://uri', 'label': 'CC BY 4.0', 'category': 'LICENSE'
    })

    # Test update_logo_license with a mocked Admin.update_file_license to avoid DB issues
    with patch('histarchexplorer.models.admin.Admin.update_file_license'):
        rv = authenticated_client.post('/admin/update_logo_license', data={
            'filename': 'test.png', 'license_id': '1', 'attribution': 'Test'
        }, follow_redirects=True)
        assert rv.status_code == 200
    
    # Test delete_license with a mocked Admin.delete_license
    with patch('histarchexplorer.models.admin.Admin.delete_license'):
        rv = authenticated_client.post('/admin/delete_license/1', follow_redirects=True)
        assert rv.status_code == 200
    
    # Test restore_db with mock
    data = {'sql_file': (io.BytesIO(b"SELECT 1;"), 'test.sql')}
    with patch('subprocess.run') as mock_run:
        rv = authenticated_client.post('/admin/restore_db', data=data, content_type='multipart/form-data', follow_redirects=True)
        assert rv.status_code == 200
        assert mock_run.called
    
    # Test delete_link
    rv = authenticated_client.get('/admin/delete_link/1/sidebar-general/0', follow_redirects=True)
    assert rv.status_code == 200
    
    # Test add_link
    rv = authenticated_client.get('/admin/add_link/?domain=1&property=1&range=1&role=1', follow_redirects=True)
    assert rv.status_code == 200
    
    # Test delete_map
    rv = authenticated_client.get('/admin/delete_map/1', follow_redirects=True)
    assert rv.status_code == 200
    
    # Test sortlinks
    rv = authenticated_client.post('/sortlinks', data={'order': '1,2,3'}, follow_redirects=True)
    assert rv.status_code == 200
    
    # Test reset
    rv = authenticated_client.get('/reset', follow_redirects=True)
    assert rv.status_code == 200
    
    # Test clear-cache
    rv = authenticated_client.get('/admin/clear-cache', follow_redirects=True)
    assert rv.status_code == 200
    
    # Test warm-entity-cache
    with patch('subprocess.Popen'):
        rv = authenticated_client.get('/admin/warm-entity-cache', follow_redirects=True)
        assert rv.status_code == 200

def test_admin_file_management(authenticated_client: FlaskClient):
    types = ['logo', 'asset', 'team', 'icon']
    for t in types:
        data = {'file': (io.BytesIO(b"data"), 'test.png'), 'file_type': t}
        rv = authenticated_client.post('/admin/upload_file', data=data, content_type='multipart/form-data', follow_redirects=True)
        assert rv.status_code == 200
        
        rv = authenticated_client.post('/admin/rename_file', data={
            'old_name': 'test.png', 'new_name': 'new.png', 'file_type': t
        }, follow_redirects=True)
        assert rv.status_code == 200
        
        rv = authenticated_client.post('/admin/delete_file', data={
            'filename': 'new.png', 'file_type': t
        }, follow_redirects=True)
        assert rv.status_code == 200

def test_admin_asset_specific(authenticated_client: FlaskClient):
    rv = authenticated_client.post('/admin/rename_asset', data={'old_name': 'a', 'new_name': 'b'}, follow_redirects=True)
    assert rv.status_code == 200
    
    rv = authenticated_client.post('/admin/delete_asset', data={'filename': 'b'}, follow_redirects=True)
    assert rv.status_code == 200
    
    rv = authenticated_client.post('/admin/update_asset_license', data={
        'filename': 'a', 'license_id': '1', 'attribution': 'T'
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_admin_cache_routes(authenticated_client: FlaskClient):
    with patch('subprocess.Popen'):
        rv = authenticated_client.get('/admin/warm-entity-cache', follow_redirects=True)
        assert rv.status_code == 200
        
    rv = authenticated_client.get('/admin/refresh-entity-cache', follow_redirects=True)
    assert rv.status_code == 200
    
    rv = authenticated_client.get('/admin/refresh-system-cache', follow_redirects=True)
    assert rv.status_code == 200
    
    rv = authenticated_client.get('/admin/clear-cache', follow_redirects=True)
    assert rv.status_code == 200

def test_admin_view_with_entry(authenticated_client: FlaskClient):
    # Test admin view with tab and entry
    rv = authenticated_client.get('/admin/nav-projects/1')
    assert rv.status_code == 200

def test_admin_more_tabs(authenticated_client: FlaskClient):
    # Test delete_entry with various tabs to cover the match/case
    tabs = [
        'nav-main-project', 'nav-projects', 'nav-persons', 'nav-institutions',
        'nav-attributes', 'sidebar-maps', 'sidebar-index-page-options',
        'sidebar-database', 'sidebar-cache-options', 'sidebar-content-group',
        'sidebar-logo-management', 'sidebar-icon-management',
        'sidebar-menu-management', 'sidebar-footer-content',
        'sidebar-file-management-group', 'sidebar-assets',
        'sidebar-legal-notice', 'sidebar-licenses', 'sidebar-team',
        'sidebar-about-publications', 'sidebar-colors', 'sidebar-type-divisions',
        'sidebar-visibility-settings'
    ]
    with patch('histarchexplorer.models.admin.Admin.delete_entry'):
        for tab in tabs:
            rv = authenticated_client.get(f'/admin/delete_entry/999/{tab}', follow_redirects=True)
            assert rv.status_code == 200

def test_update_general_settings_with_id(authenticated_client: FlaskClient):
    rv = authenticated_client.post('/admin/update_general_settings/1', data={
        'site_title': 'T', 'contact_email': 'e@e.com', 'case_study_id': '0'
    }, follow_redirects=True)
    assert rv.status_code == 200
