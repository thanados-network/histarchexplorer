import psycopg2.extras
from flask import g
from histarchexplorer import app, connect
from histarchexplorer.models.settings import Settings


def test_case_study_type_id_list_reproduction():
    with app.app_context():
        g.db = connect(app.config['DATABASE_NAME'])
        g.cursor = g.db.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)

        # Test 1: case_study_type_id is list [8240]
        g.cursor.execute(
            """
            INSERT INTO tng.system_settings (key, value)
            VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """, ("case_study_type_id", psycopg2.extras.Json([8240])))

        # Test 2: shown_types is single int 1234 instead of list
        g.cursor.execute(
            """
            INSERT INTO tng.system_settings (key, value)
            VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """, ("shown_types", psycopg2.extras.Json(1234)))

        # Test 3: index_map is string "5" instead of int
        g.cursor.execute(
            """
            INSERT INTO tng.system_settings (key, value)
            VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """, ("index_map", psycopg2.extras.Json("5")))

        # Test 4: legal_notice is invalid structure (e.g. integer 99)
        g.cursor.execute(
            """
            INSERT INTO tng.system_settings (key, value)
            VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """, ("legal_notice", psycopg2.extras.Json(99)))

        settings = Settings.load_from_db()
        assert settings.case_study_type_id == 8240
        assert settings.shown_types == [1234]
        assert settings.index_map == 5
        assert settings.legal_notice == {}
