from typing import Any, NamedTuple

import psycopg2.extras
from flask import g


def create_settings_table() -> None:
    g.cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS
            tng.system_settings
        (
            key   TEXT PRIMARY KEY,
            value JSONB NOT NULL
        ); """)


def get_settings() -> NamedTuple:
    g.cursor.execute("SELECT key, value FROM tng.system_settings")
    return g.cursor.fetchall()


def set_default_settings(key: str, value: Any) -> None:
    g.cursor.execute(
        """
        INSERT INTO tng.system_settings (key, value)
        VALUES (%s, %s)
        ON CONFLICT (key) DO NOTHING
        """, (key, psycopg2.extras.Json(value)))


def save_settings(key: str, value: Any) -> None:
    g.cursor.execute(
        """
                INSERT INTO tng.system_settings (key, value)
                VALUES (%s, %s)
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """, (key, psycopg2.extras.Json(value)))
