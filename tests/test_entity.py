from flask import url_for

from histarchexplorer import app


def test_entity(client):
    with app.app_context():
        rv = client.get(url_for('entity', id_=50505))
        assert rv.status_code == 200
        assert b"Loading" in rv.data

        rv = client.get(url_for('get_entity', id_=50505, tab_name='overview'))
        assert rv.status_code == 200
        assert b"Thunau Obere Holzwiese" in rv.data

        rv = client.get(url_for('get_entity', id_=50505, tab_name='map'))
        assert rv.status_code == 200
        assert b"Thunau Obere Holzwiese" in rv.data


        rv = client.get(url_for('entities'))
        assert rv.status_code == 200
        assert b"Name" in rv.data
