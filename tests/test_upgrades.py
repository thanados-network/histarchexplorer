import sys
from pathlib import Path
from unittest.mock import patch

import psycopg2
import pytest

from histarchexplorer import app
from install.upgrade import main as run_upgrade


@pytest.fixture()
def db_cursor():
    conn = psycopg2.connect(
        dbname=app.config['DATABASE_NAME'],
        user=app.config['DATABASE_USER'],
        password=app.config['DATABASE_PASS'],
        host=app.config['DATABASE_HOST'],
        port=app.config['DATABASE_PORT'])
    conn.autocommit = True
    cur = conn.cursor()
    yield cur
    cur.close()
    conn.close()


def test_upgrades_all_scenarios(db_cursor, capsys):
    # Setup paths for fake sql files
    upgrade_dir = Path(app.root_path).parent / 'install' / 'upgrade'
    file_98 = upgrade_dir / '98.0.0.sql'
    file_99 = upgrade_dir / '99.0.0.sql'
    file_rollback = upgrade_dir / '97.0.0.sql'

    real_sql_files = list(upgrade_dir.glob('*.sql'))
    backed_up = []

    try:
        # Temporarily hide all real migration SQL files
        for sql_file in real_sql_files:
            bak_file = sql_file.with_suffix('.sql.bak')
            if not bak_file.exists():
                sql_file.rename(bak_file)
                backed_up.append((sql_file, bak_file))

        # 1. Dynamic Initialization Scenario
        # Drop schema migrations table
        db_cursor.execute("""
            DROP TABLE IF EXISTS tng.schema_migrations CASCADE;
        """)

        # Run upgrade script - should recreate the table
        run_upgrade()

        # Verify table exists and is empty (since 0.4.0.sql was hidden)
        db_cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'tng'
                AND table_name = 'schema_migrations')
        """)
        assert db_cursor.fetchone()[0] is True

        db_cursor.execute("""
            SELECT version FROM tng.schema_migrations;
        """)
        versions = {row[0] for row in db_cursor.fetchall()}
        assert len(versions) == 0

        # Clear stdout
        capsys.readouterr()

        # 2. Sequential Version Application Scenario
        # We write 99.0.0 first, then 98.0.0 to verify semantic sort.
        # If 99 was run first, it would fail since 98 creates the table.
        with file_98.open('w') as f:
            f.write("""
                CREATE TABLE tng.test_upgrade_order (step integer);
                INSERT INTO tng.test_upgrade_order (step) VALUES (98);
            """)

        with file_99.open('w') as f:
            f.write("""
                INSERT INTO tng.test_upgrade_order (step) VALUES (99);
            """)

        run_upgrade()

        # Verify sequential application succeeded and correct
        # order was maintained
        db_cursor.execute("""
            SELECT step FROM tng.test_upgrade_order ORDER BY step;
        """)
        steps = [row[0] for row in db_cursor.fetchall()]
        assert steps == [98, 99]

        # 3. Transaction Rollback Scenario
        # 97.0.0 is older than 98/99 but we can mark it unapplied.
        with file_rollback.open('w') as f:
            f.write("""
                CREATE TABLE tng.test_rollback_table (id integer);
                INVALID SQL STATEMENT;
            """)

        with pytest.raises(Exception):
            run_upgrade()

        # Verify table from 97.0.0 was rolled back and does not exist
        db_cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'tng'
                AND table_name = 'test_rollback_table')
        """)
        assert db_cursor.fetchone()[0] is False

        # Verify 97.0.0 is not in schema_migrations
        db_cursor.execute("""
            SELECT version FROM tng.schema_migrations
            WHERE version = '97.0.0';
        """)
        assert db_cursor.fetchone() is None

        # 4. Idempotency Scenario
        # Remove the failing 97.0.0 migration so upgrade is clean
        file_rollback.unlink()

        # Clear stdout
        capsys.readouterr()

        # Run upgrade again
        run_upgrade()

        # Run upgrade once more to verify idempotency message
        capsys.readouterr()
        run_upgrade()
        captured = capsys.readouterr()
        assert "Database is up to date" in captured.out

    finally:
        # Restore original SQL files
        for sql_file, bak_file in backed_up:
            if bak_file.exists():
                bak_file.rename(sql_file)

        # Cleanup fake files
        if file_98.exists():
            file_98.unlink()
        if file_99.exists():
            file_99.unlink()
        if file_rollback.exists():
            file_rollback.unlink()

        # Cleanup created DB tables
        db_cursor.execute("""
            DROP TABLE IF EXISTS tng.test_upgrade_order CASCADE;
        """)
        db_cursor.execute("""
            DROP TABLE IF EXISTS tng.test_rollback_table CASCADE;
        """)


def test_get_pending_migrations_helper(db_cursor) -> None:
    """Verify that get_pending_migrations helper functions correctly."""
    from install.upgrade import get_pending_migrations
    upgrade_dir = Path(app.root_path).parent / 'install' / 'upgrade'
    file_99 = upgrade_dir / '99.9.9.sql'

    try:
        # Verify 99.9.9 is not currently pending
        pending_before = get_pending_migrations(db_cursor)
        assert '99.9.9' not in pending_before

        # Write fake upgrade file
        with file_99.open('w') as f:
            f.write("SELECT 1;")

        pending_after = get_pending_migrations(db_cursor)
        assert '99.9.9' in pending_after

    finally:
        if file_99.exists():
            file_99.unlink()


def test_ui_notification_banner_authenticated(
    authenticated_client) -> None:
    """Verify UI warning banner behaves correctly for admin users."""
    with patch(
        'install.upgrade.get_pending_migrations',
        return_value=['99.9.9']):
        # Test authenticated client has the red banner
        response = authenticated_client.get('/')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert "Database upgrade required!" in html
        assert "99.9.9" in html
        assert "uv run python install/upgrade.py" in html

    with patch(
        'install.upgrade.get_pending_migrations',
        return_value=[]):
        # Check that banner disappears when no upgrades are pending
        response_no_upgrades = authenticated_client.get('/')
        assert response_no_upgrades.status_code == 200
        html_no = response_no_upgrades.data.decode('utf-8')
        assert "Database upgrade required!" not in html_no


def test_ui_notification_banner_anonymous(client) -> None:
    """Verify that UI warning banner is hidden for anonymous users."""
    with patch(
        'install.upgrade.get_pending_migrations',
        return_value=['99.9.9']):
        # Test unauthenticated client does NOT see the red banner
        response_anon = client.get('/')
        if response_anon.status_code == 200:
            html_anon = response_anon.data.decode('utf-8')
            assert "Database upgrade required!" not in html_anon
        elif response_anon.status_code == 302:
            assert response_anon.location.endswith('/login')
