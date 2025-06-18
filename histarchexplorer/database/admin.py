from typing import Any

from flask import g


def get_config_properties() -> Any:
    g.cursor.execute(
        '''
        SELECT id, name, domain, range, 'direct' AS direction
        FROM tng.config_properties
        UNION ALL
        SELECT id, name_inv, range, domain, 'inverse' AS direction
        FROM tng.config_properties''')
    return g.cursor.fetchall()


def set_hidden_entities(entities: list[str]) -> None:
    g.cursor.execute(
        'UPDATE tng.settings SET hidden_entities = %s',
        (entities,))


def set_shown_entities(entities: list[str]) -> None:
    g.cursor.execute(
        'UPDATE tng.settings SET shown_entities = %s',
        (entities,))


def set_index_background(settings: dict[str, str]) -> None:
    g.cursor.execute(
        """
        UPDATE tng.settings
        SET (index_map, index_img, img_map, greyscale) = (%s, %s, %s, %s)""", (
            settings['index_map'],
            settings['index_img'],
            settings['img_map'],
            settings['greyscale']))
