from pathlib import Path
from typing import Any

import psycopg2

from histarchexplorer import app


def run_sql_file(cursor: Any, filepath: Path) -> None:
    with filepath.open('r') as f:
        sql = f.read()
        cursor.execute(sql)
        print(f"Executed {filepath.name}")


def main() -> None:
    # Connection config
    conn = psycopg2.connect(
        dbname=app.config['DATABASE_NAME'],
        user=app.config['DATABASE_USER'],
        password=app.config['DATABASE_PASS'],
        host=app.config['DATABASE_HOST'],
        port=app.config['DATABASE_PORT'])

    # Base directory is where this script resides
    base_dir = Path(__file__).resolve().parent
    sql_files = ['1_structure.sql', '2_data_model.sql']
    sql_paths = [base_dir / file for file in sql_files]

    try:
        with conn:
            with conn.cursor() as cur:
                for sql_path in sql_paths:
                    run_sql_file(cur, sql_path)
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == '__main__':
    main()
