import os
import subprocess
from pathlib import Path

from histarchexplorer import app

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
