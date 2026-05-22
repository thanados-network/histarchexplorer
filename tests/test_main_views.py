import pytest
from unittest.mock import patch, MagicMock
from flask.testing import FlaskClient
from histarchexplorer.models.settings import Settings

def test_index_page(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.models.settings.Settings.load_from_db') as mock_settings:
        settings = Settings()
        settings.access_restriction = False
        mock_settings.return_value = settings
        
        rv = authenticated_client.get('/')
        assert rv.status_code == 200

def test_set_language(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/language=de', headers={'Referer': '/'})
    assert rv.status_code == 302

def test_type_tree(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.api.api_access.ApiAccess.get_type_tree') as mock_get:
        mock_get.return_value = {'tree': []}
        rv = authenticated_client.get('/type-tree')
        assert rv.status_code == 200

def test_files_of_entities(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.api.api_access.ApiAccess.get_files_of_entities') as mock_get:
        mock_get.return_value = {'files': []}
        rv = authenticated_client.get('/files-of-entities')
        assert rv.status_code == 200

def test_entities_count(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.api.api_access.ApiAccess.get_entities_count_by_case_studies') as mock_get:
        mock_get.return_value = {'counts': {}}
        rv = authenticated_client.get('/entities-count')
        assert rv.status_code == 200
