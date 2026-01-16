from flask import url_for
from flask.testing import FlaskClient

from histarchexplorer import app


def test_entity(client: FlaskClient) -> None:
    with app.app_context():
        rv = client.get(url_for('entity_view', id_=50505))
        assert rv.status_code == 200
        assert b"Loading" in rv.data

        rv = client.get(url_for('get_entity', id_=50505, tab_name='overview'))
        assert rv.status_code == 200
        assert b"Thunau Obere Holzwiese" in rv.data

        rv = client.get(url_for('get_entity', id_=50505, tab_name='map'))
        assert rv.status_code == 200
        assert b"Thunau Obere Holzwiese" in rv.data

        rv = client.get(url_for('get_entity', id_=50505, tab_name='subunits'))
        assert rv.status_code == 200
        assert b"Agilolf" in rv.data

        rv = client.get(url_for('get_entity', id_=50505, tab_name='media'))
        assert rv.status_code == 200
        assert b"iiif_manifest" in rv.data

        rv = client.get(url_for('get_entity', id_=59099, tab_name='overview'))
        assert rv.status_code == 200
        assert b"Grave 073" in rv.data

        rv = client.get(url_for('get_entity', id_=77703, tab_name='map'))
        assert rv.status_code == 200
        assert b"G073S1" in rv.data

        rv = client.get(url_for('get_entity', id_=102031, tab_name='overview'))
        assert rv.status_code == 200
        assert b"G043F01" in rv.data

        # Test main image
        rv = client.get(url_for('get_entity', id_=128351, tab_name='overview'))
        assert rv.status_code == 200
        assert b"ERC Synergy Grant HistoGenes" in rv.data

        # Test alias
        rv = client.get(url_for('get_entity', id_=13800, tab_name='overview'))
        assert rv.status_code == 200
        assert b"Abbey Chiemsee" in rv.data

        # Test minus dates
        rv = client.get(url_for('get_entity', id_=230071, tab_name='overview'))
        assert rv.status_code == 200
        assert b"Mitterhof" in rv.data

        # Test glb, wepb and mp4
        rv = client.get(url_for('get_entity', id_=196952, tab_name='overview'))
        assert rv.status_code == 200
        assert b"Venus of Willendorf" in rv.data

        # Test pdf
        rv = client.get(url_for('get_entity', id_=203599, tab_name='overview'))
        assert rv.status_code == 200
        assert b"Reichartz" in rv.data

        rv = client.get(url_for('entity_view', id_=50505, tab_name='wrong'))
        assert rv.status_code == 404

        rv = client.get(url_for('get_entity', id_=50505, tab_name='wrong'))
        assert rv.status_code == 404
