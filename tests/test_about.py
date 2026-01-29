from flask import url_for
from flask.testing import FlaskClient

from histarchexplorer import app


def test_about_page(client: FlaskClient) -> None:
    with app.app_context():
        rv = client.get(url_for('about'))
        assert rv.status_code == 200
        assert b"TEAM" in rv.data
