from typing import Any, NamedTuple

from flask import g


def get_shown_classes() -> Any:
    g.cursor.execute(
        'SELECT shown_classes '
        'FROM tng.settings '
        'LIMIT 1')
    result = g.cursor.fetchone()
    return result[0] or []


def get_hidden_classes() -> Any:
    g.cursor.execute(
        'SELECT hidden_classes '
        'FROM tng.settings '
        'LIMIT 1')
    result = g.cursor.fetchone()
    return result[0] or []

def get_main_image_table() -> dict[int, int]:
    main_image = {}
    g.cursor.execute(
        'SELECT '
        '   entity_id,'
        '   image_id '
        'FROM web.entity_profile_image')
    for row in g.cursor.fetchall():
        main_image[row[0]] = row[1]
    return main_image


def get_settings() -> NamedTuple:
    g.cursor.execute("SELECT * FROM tng.settings LIMIT 1")
    return g.cursor.fetchone()
