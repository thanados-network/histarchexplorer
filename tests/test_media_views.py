from flask.testing import FlaskClient


def test_view_media(authenticated_client: FlaskClient) -> None:
    render_types = ['image', '3d_model', 'video', 'pdf', 'svg', 'unknown']
    for rt in render_types:
        rv = authenticated_client.get(f'/view/{rt}/1')
        assert rv.status_code == 200

    rv_xss = authenticated_client.get('/view/<img src=x onerror=alert(1)>/1')
    assert rv_xss.status_code == 200
    assert b'<img src=x' not in rv_xss.data
    assert b'&lt;img src=x' in rv_xss.data
