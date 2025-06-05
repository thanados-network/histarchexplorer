from typing import Any

from flask import g


def get_map_settings() -> Any:
    g.cursor.execute(
        'SELECT index_img, index_map, img_map, greyscale '
        'FROM tng.settings '
        'LIMIT 1')
    return g.cursor.fetchone()

def get_shown_entities() -> Any:
    g.cursor.execute(
        'SELECT shown_entities '
        'FROM tng.settings '
        'LIMIT 1')
    return g.cursor.fetchone().shown_entities

def get_hidden_entities() -> Any:
    g.cursor.execute(
        'SELECT hidden_entities '
        'FROM tng.settings '
        'LIMIT 1')
    return g.cursor.fetchone().hidden_entities

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
