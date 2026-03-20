from flask.testing import FlaskClient


def test_about(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/about')
    assert rv.status_code == 200


def test_about_with_slug(
        authenticated_client: FlaskClient) -> None:
    # 'thanados-netzwerk' is likely the slug for the main project in the test data
    rv = authenticated_client.get(
        '/about/thanados-netzwerk')
    assert rv.status_code == 200


def test_about_invalid_slug(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get(
        '/about/invalid-slug')
    assert rv.status_code == 302
    assert rv.location.endswith('/about')


def test_publications(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/publications')
    assert rv.status_code == 200


def test_about_redirects_unauthenticated(
        client: FlaskClient) -> None:
    rv = client.get('/about')
    assert rv.status_code == 302
