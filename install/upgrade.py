import re
from pathlib import Path
from typing import Any

import psycopg2


def parse_version(filename: str) -> tuple[int, ...]:
    """Parse version tuple from SQL file name.

    e.g. '0.4.0.sql' -> (0, 4, 0)
    """
    match = re.search(r'(\d+)\.(\d+)\.(\d+)', filename)
    if match:
        return tuple(map(int, match.groups()))
    return (0, 0, 0)


def create_migrations_table(cursor: Any) -> None:
    """Create the schema_migrations table if it does not exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tng.schema_migrations (
            version VARCHAR(50) PRIMARY KEY,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)


def get_applied_versions(cursor: Any) -> set[str]:
    """Fetch the set of already applied migration versions."""
    cursor.execute("SELECT version FROM tng.schema_migrations;")
    return {row[0] for row in cursor.fetchall()}


def get_pending_migrations(cursor: Any) -> list[str]:
    """Find and return list of unapplied migration version strings."""
    create_migrations_table(cursor)
    applied = get_applied_versions(cursor)

    base_dir = Path(__file__).resolve().parent / 'upgrade'
    sql_files = list(base_dir.glob('[0-9]*.[0-9]*.[0-9]*.sql'))

    pending = []
    for filepath in sql_files:
        match = re.search(r'(\d+\.\d+\.\d+)', filepath.name)
        if match:
            version_str = match.group(1)
            if version_str not in applied:
                version_tuple = parse_version(filepath.name)
                pending.append((version_tuple, version_str))

    pending.sort(key=lambda x: x[0])
    return [version_str for _, version_str in pending]


def apply_migration(
    cursor: Any,
    filepath: Path,
    version: str
) -> None:
    """Run SQL from filepath and record version in schema_migrations."""
    with filepath.open('r') as f:
        sql = f.read()

    cursor.execute(sql)
    cursor.execute(
        "INSERT INTO tng.schema_migrations (version) VALUES (%s);",
        (version,))
    print(f"Applied migration: {filepath.name}")


def main() -> None:
    """Discover, sort, and apply unapplied SQL upgrades."""
    from histarchexplorer import app

    conn = psycopg2.connect(
        dbname=app.config['DATABASE_NAME'],
        user=app.config['DATABASE_USER'],
        password=app.config['DATABASE_PASS'],
        host=app.config['DATABASE_HOST'],
        port=app.config['DATABASE_PORT'])

    base_dir = Path(__file__).resolve().parent / 'upgrade'
    sql_files = list(base_dir.glob('[0-9]*.[0-9]*.[0-9]*.sql'))

    try:
        with conn:
            with conn.cursor() as cur:
                create_migrations_table(cur)
                applied = get_applied_versions(cur)

        pending = []
        for filepath in sql_files:
            match = re.search(r'(\d+\.\d+\.\d+)', filepath.name)
            if match:
                version_str = match.group(1)
                if version_str not in applied:
                    version_tuple = parse_version(filepath.name)
                    pending.append((
                        version_tuple,
                        version_str,
                        filepath))

        pending.sort(key=lambda x: x[0])

        if not pending:
            print("Database is up to date. No pending migrations.")
            return

        for _, version_str, filepath in pending:
            with conn:
                with conn.cursor() as cur:
                    apply_migration(cur, filepath, version_str)

        print("Database upgrade completed successfully.")
    except Exception as e:
        print(f"Upgrade failed: {e}")
        raise
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == '__main__':
    main()
