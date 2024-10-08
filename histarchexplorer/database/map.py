from typing import Any

from flask import g


def get_map_tilestring(data: Any) -> Any:
    g.cursor.execute(
        'SELECT tilestring '
        'FROM tng.maps '
        f'WHERE id={data.index_map}')
    return g.cursor.fetchone()

def get_base_map() -> Any:
    g.cursor.execute('SELECT * FROM tng.maps ORDER BY sortorder')
    return g.cursor.fetchall()

def get_base_map_by_id(map_id: int) -> Any:
    g.cursor.execute('SELECT * FROM tng.maps WHERE id = %s', (map_id,))
    return g.cursor.fetchone()
