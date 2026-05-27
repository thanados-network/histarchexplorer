import pytest
from unittest.mock import patch, MagicMock
from flask.testing import FlaskClient
from histarchexplorer.models.settings import Settings

def test_about_page(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.models.settings.Settings.load_from_db') as mock_settings:
        settings = Settings()
        settings.access_restriction = False
        mock_settings.return_value = settings
        
        rv = authenticated_client.get('/about')
        assert rv.status_code == 200

def test_publications_page(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.models.settings.Settings.load_from_db') as mock_settings:
        settings = Settings()
        settings.access_restriction = False
        mock_settings.return_value = settings
        
        rv = authenticated_client.get('/publications')
        assert rv.status_code == 200

def test_outcome_page(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.models.settings.Settings.load_from_db') as mock_settings:
        settings = Settings()
        settings.access_restriction = False
        mock_settings.return_value = settings
        
        rv = authenticated_client.get('/outcome')
        assert rv.status_code == 200
