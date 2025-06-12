import os

import pytest
import psycopg2
from histarchexplorer import app as flask_app_instance

@pytest.fixture(scope='session')
def flask_app():
    """
    Fixture to set up and tear down the Flask application for testing.
    This fixture has a 'session' scope, meaning it runs once per test session.
    """
    print("\nSetting up Flask app for testing...")
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
            sql_path = os.path.join(app.root_path, 'sql', 'admin_reset.sql')
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
    """
    Fixture to provide a test client for the Flask app.
    This fixture has a 'function' scope, meaning it runs before each test function.
    It uses the 'flask_app' fixture, ensuring the app is set up.
    """
    print("Setting up Flask test client...")
    with flask_app.test_client() as client:
        with client.session_transaction() as sess:
            sess.clear()
        yield client
    print("Tearing down Flask test client.")
