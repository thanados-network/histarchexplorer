from flask import url_for

from histarchexplorer import app


def test_browse(client):
    with app.app_context():
        rv = client.get(url_for('entities'))
        assert rv.status_code == 200
        assert b"Name" in rv.data
