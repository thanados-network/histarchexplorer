from flask.testing import FlaskClient


def test_outcome(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/outcome')
    assert rv.status_code == 200


def test_outcome_redirects_unauthenticated(
        client: FlaskClient) -> None:
    rv = client.get('/outcome')
    assert rv.status_code == 302
