import re
from pathlib import Path
from typing import Any

import psycopg2

from histarchexplorer import app


def run_sql_file(cursor: Any, filepath: Path) -> None:
    with filepath.open('r') as f:
        sql = f.read()
        cursor.execute(sql)
        print(f"Executed {filepath.name}")


def seed_migrations(cursor: Any, upgrade_dir: Path) -> None:
    """Create the migration table and mark existing migrations as applied."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tng.schema_migrations (
            version VARCHAR(50) PRIMARY KEY,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    sql_files = list(upgrade_dir.glob('[0-9]*.[0-9]*.[0-9]*.sql'))
    for filepath in sql_files:
        match = re.search(r'(\d+\.\d+\.\d+)', filepath.name)
        if match:
            version_str = match.group(1)
            cursor.execute("""
                INSERT INTO tng.schema_migrations (version)
                VALUES (%s)
                ON CONFLICT (version) DO NOTHING;
            """, (version_str,))
            print(f"Seeded migration version {version_str} as applied.")


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
                seed_migrations(cur, base_dir / 'upgrade')
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == '__main__':
    main()
