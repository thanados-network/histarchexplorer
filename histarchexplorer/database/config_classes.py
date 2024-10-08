from typing import Any

from flask import g


def get_config_classes() -> Any:
    g.cursor.execute('SELECT * FROM tng.config_classes')
    return g.cursor.fetchall()
