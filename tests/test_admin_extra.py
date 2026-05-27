import pytest
from unittest.mock import patch, MagicMock
from flask.testing import FlaskClient
import io
import os

def test_delete_entry_main_project(authenticated_client: FlaskClient):
    with patch('histarchexplorer.models.admin.Admin.get_config_class_by_id') as mock_get:
        mock_get.return_value = 5 # Main Project
        rv = authenticated_client.get('/admin/delete_entry/1/sidebar-team', follow_redirects=True)
        assert b'Main Project cannot be deleted' in rv.data

from histarchexplorer.models.settings import Settings

def test_add_available_color_edge_cases(authenticated_client: FlaskClient):
    # Invalid Hex
    rv = authenticated_client.post('/admin/add_available_color', data={'new_color': 'invalid'}, follow_redirects=True)
    assert b'Invalid HEX code' in rv.data
    
    # Already exists
    settings = Settings()
    settings.available_colors = ['#FFFFFF']
    with patch('histarchexplorer.models.settings.Settings.load_from_db', return_value=settings):
        rv = authenticated_client.post('/admin/add_available_color', data={'new_color': '#FFFFFF'}, follow_redirects=True)
        assert b'Color already exists' in rv.data

def test_admin_save_errors(authenticated_client: FlaskClient):
    settings = Settings()
    with patch.object(Settings, 'save_to_db', side_effect=Exception("Save failed")):
        with patch('histarchexplorer.models.settings.Settings.load_from_db', return_value=settings):
            # update_type_divisions
            rv = authenticated_client.post('/admin/update_type_divisions', data={'label_1': 'Test', 'ids_1': '1'}, follow_redirects=True)
            assert b'Error updating type divisions' in rv.data
            
            # update_entity_colors
            rv = authenticated_client.post('/admin/update_entity_colors', data={'entity_colors-place': '#000000'}, follow_redirects=True)
            assert b'Error updating entity colors' in rv.data
            
            # add_available_color
            rv = authenticated_client.post('/admin/add_available_color', data={'new_color': '#112233'}, follow_redirects=True)
            assert b'Error adding color' in rv.data
            
            # delete_available_color
            settings.available_colors = ['#112233']
            rv = authenticated_client.post('/admin/delete_available_color', data={'color_to_delete': '#112233'}, follow_redirects=True)
            assert b'Error deleting color' in rv.data
            
            # update_menu_management
            rv = authenticated_client.post('/admin/update_menu_management', data={}, follow_redirects=True)
            assert b'Error updating menu settings' in rv.data
            
            # update_legal_notice
            rv = authenticated_client.post('/admin/update_legal_notice', data={}, follow_redirects=True)
            assert b'Error updating settings' in rv.data

def test_logo_management_edge_cases(authenticated_client: FlaskClient):
    # rename_logo invalid request
    rv = authenticated_client.post('/admin/rename_logo', data={}, follow_redirects=True)
    assert b'Invalid request for renaming' in rv.data
    
    # rename_logo default logo
    with patch('os.path.exists') as mock_exists:
        mock_exists.side_effect = lambda p: 'static' in p
        rv = authenticated_client.post('/admin/rename_logo', data={'old_name': 'default.png', 'new_name': 'new.png'}, follow_redirects=True)
        assert b'Cannot rename default logos' in rv.data
        
    # rename_logo file not found
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = False
        rv = authenticated_client.post('/admin/rename_logo', data={'old_name': 'missing.png', 'new_name': 'new.png'}, follow_redirects=True)
        assert b'Original file not found' in rv.data

    # delete_logo no filename
    rv = authenticated_client.post('/admin/delete_logo', data={}, follow_redirects=True)
    assert b'No filename specified for deletion' in rv.data

def test_set_favicon_edge_cases(authenticated_client: FlaskClient):
    # no filename
    rv = authenticated_client.post('/admin/set_favicon', data={}, follow_redirects=True)
    assert b'No filename specified' in rv.data
    
    # PIL error
    with patch('os.path.exists', return_value=True), \
         patch('PIL.Image.open') as mock_open:
        mock_open.side_effect = Exception("PIL error")
        rv = authenticated_client.post('/admin/set_favicon', data={'filename': 'test.png'}, follow_redirects=True)
        assert b'Error creating favicon' in rv.data

def test_update_type_divisions_invalid_id(authenticated_client: FlaskClient):
    rv = authenticated_client.post('/admin/update_type_divisions', data={'label_1': 'Test', 'ids_1': 'invalid'}, follow_redirects=True)
    assert b'Invalid ID format' in rv.data
