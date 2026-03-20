from typing import Any

from flask import g


def get_map_tilestring(index_map: int) -> str | None:
    g.cursor.execute(
        'SELECT tilestring '
        'FROM tng.maps '
        'WHERE id = %s', (index_map,))
    row = g.cursor.fetchone()
    return row['tilestring'] if row else None


def get_maps() -> tuple[str]:
    g.cursor.execute('SELECT * FROM tng.maps ORDER BY sortorder')
    return g.cursor.fetchall()


# def get_base_map_by_id(map_id: int) -> Any:
#     g.cursor.execute('SELECT * FROM tng.maps WHERE id = %s', (map_id,))
#     return g.cursor.fetchone()


def check_if_map_id_exist(id_: int) -> bool:
    g.cursor.execute(
        'SELECT 1 FROM tng.maps WHERE id = %(id)s',
        {'id': id_})
    return g.cursor.fetchone() is not None
