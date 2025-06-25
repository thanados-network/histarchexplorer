from typing import Any

from flask import g


def get_config_types_sql() -> Any:
    g.cursor.execute('SELECT * FROM tng.types')
    return g.cursor.fetchall()
