from typing import Any

from flask import g


def get_config_classes_sql() -> Any:
    g.cursor.execute('SELECT * FROM tng.classes')
    return g.cursor.fetchall()
