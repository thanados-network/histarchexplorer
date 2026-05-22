import pytest
from flask.testing import FlaskClient

def test_view_media(authenticated_client: FlaskClient) -> None:
    render_types = ['image', '3d_model', 'video', 'pdf', 'svg', 'unknown']
    for rt in render_types:
        rv = authenticated_client.get(f'/view/{rt}/1')
        assert rv.status_code == 200
