from flask import url_for

from histarchexplorer import app


def test_login(client):
    with app.app_context():
        rv = client.get(url_for('login'))
        assert b"Username" in rv.data

        rv = client.post(
            url_for('login'),
            data={'username': 'Inactive', 'password': 'test'},
            follow_redirects=True)
        assert b"error inactive" in rv.data

        rv = client.post(
            url_for('login'),
            data={'username': 'Wrong', 'password': 'test'},
            follow_redirects=True)
        assert b"error username" in rv.data

        rv = client.post(
            url_for('login'),
            data={'username': 'Alice', 'password': 'Wrong'},
            follow_redirects=True)
        assert b"error wrong password" in rv.data


        rv = client.post(
            url_for('login'),
            data={'username': 'Alice', 'password': 'test'},
            follow_redirects=True)
        assert b"ENTITIES" in rv.data

        rv = client.post(
            url_for('login'),
            data={'username': 'Alice', 'password': 'test'},
            follow_redirects=True)
        assert b"TOOLS" in rv.data
