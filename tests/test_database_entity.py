from flask import g
import psycopg2.extras
from histarchexplorer.database.entity import (
    check_geom, get_first_geom, check_if_place_hierarchy)
from histarchexplorer import app, connect

def test_check_geom(client) -> None:
    with app.test_request_context():
        # Setup g.openatlas_cursor
        g.openatlas_db = connect(app.config['OPENATLAS_DATABASE_NAME'])
        g.openatlas_cursor = g.openatlas_db.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Test with an ID that probably doesn't have geom
        assert check_geom(999999) is None
        
        # We need an ID that HAS geometry to test the positive case.
        g.openatlas_cursor.execute("SELECT entity_id FROM model.gis LIMIT 1;")
        res = g.openatlas_cursor.fetchone()
        if res:
            g.openatlas_cursor.execute(
                "SELECT domain_id FROM model.link WHERE range_id = %s "
                "AND property_code = 'P53' LIMIT 1;",
                (res['entity_id'],))
            link_res = g.openatlas_cursor.fetchone()
            if link_res:
                assert check_geom(link_res['domain_id']) == link_res['domain_id']

def test_get_first_geom(client) -> None:
    with app.test_request_context():
        g.openatlas_db = connect(app.config['OPENATLAS_DATABASE_NAME'])
        g.openatlas_cursor = g.openatlas_db.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        assert get_first_geom(999999) is None

def test_check_if_place_hierarchy(client) -> None:
    with app.test_request_context():
        g.openatlas_db = connect(app.config['OPENATLAS_DATABASE_NAME'])
        g.openatlas_cursor = g.openatlas_db.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        assert check_if_place_hierarchy(999999) is False
