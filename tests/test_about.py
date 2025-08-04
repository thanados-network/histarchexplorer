from flask import url_for

from histarchexplorer import app


def test_about_page(client):
    with app.app_context():
        rv = client.get(url_for('about'))
        assert rv.status_code == 200
        assert b"TEAM" in rv.data

