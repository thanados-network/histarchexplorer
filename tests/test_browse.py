from flask import url_for
from flask.testing import FlaskClient

from histarchexplorer import app


def test_browse(client: FlaskClient) -> None:
    with app.app_context():

        rv = client.get(url_for('entities'))
        assert rv.status_code == 200
        assert b"Name" in rv.data

        rv = client.get(url_for('get_entities', tab_name='place'))
        assert rv.status_code == 200
        assert b"Name" in rv.data
