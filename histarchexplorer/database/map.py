from typing import Any

from flask import g


def get_map_server(data: Any) -> Any:
    g.cursor.execute(
        f'SELECT tilestring '
        f'FROM tng.maps '
        f'WHERE id={data.index_map}')
    return g.cursor.fetchone()
