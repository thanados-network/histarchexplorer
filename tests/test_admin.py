from flask import url_for

from histarchexplorer import app


def test_admin_page(client):
    with app.app_context():
        rv = client.get(url_for('admin'), follow_redirects=True)
        assert b"Username" in rv.data

        client.post(
                url_for('login'),
                data={'username': 'Alice', 'password': 'test'})
        rv = client.get(url_for('admin'), follow_redirects=True)
        assert b"TOOLS" in rv.data

        rv = client.get(url_for('logout'), follow_redirects=True)
        assert b'ENTITIES' in rv.data
