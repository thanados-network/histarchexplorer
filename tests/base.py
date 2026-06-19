import os
import subprocess
from pathlib import Path

import psycopg2

from histarchexplorer import app
from install.install_script import seed_migrations

INSTALL_DIR = Path(app.root_path).parent / 'install'
SQL_FILES = ['1_structure.sql', '2_data_model.sql']


def reset_test_database() -> None:
    env = os.environ.copy()
    env['PGPASSWORD'] = app.config['DATABASE_PASS']
    for sql_file in SQL_FILES:
        subprocess.run(
            ['psql',
             '-U', app.config['DATABASE_USER'],
             '-h', app.config['DATABASE_HOST'],
             '-p', str(app.config['DATABASE_PORT']),
             '-d', app.config['DATABASE_NAME'],
             '-f', str(INSTALL_DIR / sql_file)],
            env=env,
            check=True,
            capture_output=True)

    # Force English for tests
    subprocess.run(
        ['psql',
         '-U', app.config['DATABASE_USER'],
         '-h', app.config['DATABASE_HOST'],
         '-p', str(app.config['DATABASE_PORT']),
         '-d', app.config['DATABASE_NAME'],
         '-c', "UPDATE tng.system_settings SET value = '\"en\"' WHERE key = 'preferred_language';"],
        env=env,
        check=True,
        capture_output=True)

    # Seed migrations for test database
    conn = psycopg2.connect(
        dbname=app.config['DATABASE_NAME'],
        user=app.config['DATABASE_USER'],
        password=app.config['DATABASE_PASS'],
        host=app.config['DATABASE_HOST'],
        port=app.config['DATABASE_PORT'])

    try:
        with conn:
            with conn.cursor() as cur:
                seed_migrations(cur, INSTALL_DIR / 'upgrade')
    finally:
        conn.close()
