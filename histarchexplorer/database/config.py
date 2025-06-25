from typing import Any

from flask import g


def get_config_data(language: str) -> Any:
    g.cursor.execute(
        f"SELECT * FROM tng.entities ORDER BY (name->>'{language}')")
    return g.cursor.fetchall()


def check_if_config_entry_exist(id_: int) -> bool:
    g.cursor.execute(
        'SELECT 1 FROM tng.entities WHERE id = %(id)s',
        {'id': id_})
    return g.cursor.fetchone() is not None
