import os

import pytest
import psycopg2
from histarchexplorer import app as flask_app_instance

@pytest.fixture(scope='session')
def flask_app():
    app = flask_app_instance
    app.config.from_pyfile('testing.py', silent=False)
    fixture_conn = None
    try:
        fixture_conn = psycopg2.connect(
            database=app.config['DATABASE_NAME'],
            host=app.config['DATABASE_HOST'],
            user=app.config['DATABASE_USER'],
            password=app.config['DATABASE_PASS'],
            port=app.config['DATABASE_PORT'] )
        fixture_conn.autocommit = True

        with fixture_conn.cursor() as cursor:
            sql_scripts = ['reset.sql', 'add_test_user.sql']
            for script in sql_scripts:
                sql_path = os.path.join(app.root_path, 'sql', script)
                with open(sql_path, 'r', encoding='utf-8') as file:
                    sql_script = file.read()
                cursor.execute(sql_script)
        print(f"Successfully connected to test database: "
              f"{app.config['DATABASE_NAME']} and schema prepared.")
        yield app

    except psycopg2.Error as e:
        print(f"\nERROR: Could not connect to the test database! "
              f"Please ensure your test database '{app.config['DATABASE_NAME']}' "
              f"is running and accessible with the specified credentials in 'instance/testing.py'.")
        print(f"PostgreSQL Error: {e}")
        yield app
    finally:
        if fixture_conn:
            fixture_conn.close()
            print("Test database connection closed.")
        print("Tearing down Flask app.")


@pytest.fixture(scope='function')
def client(flask_app):
    with flask_app.test_client() as client:
        with client.session_transaction() as sess:
            sess.clear()
        yield client
