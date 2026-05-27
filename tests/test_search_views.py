import pytest
from unittest.mock import patch, MagicMock
from flask.testing import FlaskClient

def test_search_page(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/search')
    assert rv.status_code == 200

def test_perform_search(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.models.search.SearchService.perform_search') as mock_search:
        mock_search.return_value = [{'id': 1, 'title': 'Result 1'}]
        rv = authenticated_client.post('/search', data={
            'query': 'test',
            'category': 'all'
        })
        assert rv.status_code == 200

def test_search_live(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.models.search.SearchService.perform_live_search') as mock_search:
        mock_search.return_value = [{'id': 1, 'title': 'Live Result'}]
        rv = authenticated_client.get('/search_live?q=test')
        assert rv.status_code == 200
