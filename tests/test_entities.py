from flask.testing import FlaskClient
from unittest.mock import patch


def test_entities(
        authenticated_client: FlaskClient) -> None:
    # Mocking get_browse_list_entities which is called by return_entities
    with patch('histarchexplorer.views.entities.get_browse_list_entities') as mock_get_browse:
        mock_get_browse.return_value = {
            'totals': {'places': 10},
            'counts': {'places': [{'place': 10}]},
            'cs_ids': []
        }
        rv = authenticated_client.get('/entities')
        assert rv.status_code == 200


def test_entities_with_tab(
        authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.views.entities.get_browse_list_entities') as mock_get_browse:
        mock_get_browse.return_value = {
            'totals': {'places': 10},
            'counts': {'places': [{'place': 10}]},
            'cs_ids': []
        }
        rv = authenticated_client.get('/entities/places')
        assert rv.status_code == 200


def test_get_entities_json(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/get_entities/places')
    assert rv.status_code == 200


def test_entities_redirects_unauthenticated(
        client: FlaskClient) -> None:
    rv = client.get('/entities')
    assert rv.status_code == 302
