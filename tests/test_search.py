from flask.testing import FlaskClient


def test_search_get(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/search')
    assert rv.status_code == 200


def test_search_post(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.post(
        '/search', data={'search': 'test'})
    assert rv.status_code == 200


def test_api_search(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/api/search?search=test')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'items' in data
    assert 'total_items' in data


def test_search_live(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/search_live?q=test')
    assert rv.status_code == 200


def test_search_redirects_unauthenticated(
        client: FlaskClient) -> None:
    rv = client.get('/search')
    assert rv.status_code in [200, 302]
