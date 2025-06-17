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

        # Test main image
        rv = client.get(url_for('get_entity', id_=128351, tab_name='overview'))
        assert rv.status_code == 200
        assert b"ERC Synergy Grant HistoGenes" in rv.data

        # Test alias
        rv = client.get(url_for('get_entity', id_=13800, tab_name='overview'))
        assert rv.status_code == 200
        assert b"Abbey Chiemsee" in rv.data

        rv = client.get(url_for('entities'))
        assert rv.status_code == 200
        assert b"Name" in rv.data
