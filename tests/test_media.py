from flask.testing import FlaskClient


def test_view_media_image(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/view/image/1')
    assert rv.status_code in (200, 404)


def test_view_media_3d(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/view/3d/1')
    assert rv.status_code in (200, 404)


def test_view_media_nonexistent(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/view/image/999999')
    assert rv.status_code in (200, 404)
