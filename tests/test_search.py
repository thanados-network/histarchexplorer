from flask import url_for
from flask.testing import FlaskClient

from histarchexplorer import app


def test_search_page(client: FlaskClient) -> None:
    with app.app_context():
        rv = client.get(url_for('search'))
        assert rv.status_code == 200
        assert b"Start typing above to see" in rv.data

        rv = client.post(
            url_for('search'),
            data={
                'query': 'mist',
                'category': 'actor',
                'system_class': 'person'})
        assert b"Mistelbach" in rv.data
