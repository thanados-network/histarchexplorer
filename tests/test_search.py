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


def test_search_live(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/search_live?q=test')
    assert rv.status_code == 200


def test_search_redirects_unauthenticated(
        client: FlaskClient) -> None:
    rv = client.get('/search')
    assert rv.status_code == 302
