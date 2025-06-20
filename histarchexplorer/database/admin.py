import json
from typing import Any

from flask import g

from histarchexplorer.database.config import check_if_config_entry_exist


def get_config_properties() -> Any:
    g.cursor.execute(
        '''
        SELECT id, name, domain, range, 'direct' AS direction
        FROM tng.config_properties
        UNION ALL
        SELECT id, name_inv, range, domain, 'inverse' AS direction
        FROM tng.config_properties''')
    return g.cursor.fetchall()


def get_config_config_class_by_id(id_: int) -> int | None:
    g.cursor.execute(
        'SELECT config_class FROM tng.config WHERE id = %s',
        (id_,))
    row = g.cursor.fetchone()
    return row[0] if row else None


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
        SET index_map = %(index_map)s,
            index_img = %(index_img)s,
            img_map   = %(img_map)s,
            greyscale = %(greyscale)s
        """,
        settings)


def add_new_map(data: dict[str, str]) -> int:
    g.cursor.execute(
        '''
        INSERT INTO tng.maps
            (name, display_name, sortorder, tilestring)
        VALUES (%(name)s, %(display_name)s, %(sort_order)s, %(tile_string)s)
        RETURNING id
        ''', {
            'name': data['name'],
            'display_name': data['display_name'],
            'sort_order': data['sort_order'],
            'tile_string': data['tile_string']})

    return g.cursor.fetchone()[0]


def delete_map(map_id: int) -> None:
    g.cursor.execute(
        'DELETE FROM tng.maps WHERE id = %(map_id)s',
        {'map_id': map_id})


def update_map(data: dict[str, str]) -> None:
    g.cursor.execute(
        """
        UPDATE tng.maps
        SET name         = NULLIF(%(name)s, ''),
            display_name = NULLIF(%(display_name)s, ''),
            sortorder    = CASE
                               WHEN %(sortorder)s = '' THEN NULL
                               ELSE CAST(%(sortorder)s AS integer)
                END,
            tilestring   = NULLIF(%(tilestring)s, '')
        WHERE id = %(map_id)s
        """,
        data)


def check_if_main_project_exist() -> bool:
    g.cursor.execute("SELECT 1 FROM tng.config WHERE config_class = 5 LIMIT 1")
    return g.cursor.fetchone() is not None


def delete_entry(id_: int) -> None:
    g.cursor.execute(
        'DELETE FROM tng.config WHERE id = %(id)s',
        {'id': id_})


def create_config_entry(data: dict) -> int:
    config_class = g.config_class_map.get(data['category'])
    if config_class is None:
        raise ValueError(f"Unknown category {data['category']}")

    if config_class == 5 and check_if_main_project_exist():
        raise 404

    g.cursor.execute(
        """
        INSERT INTO tng.config
        (email, website, orcid_id, image, config_class)
        VALUES (NULLIF(%(email)s, ''),
                NULLIF(%(website)s, ''),
                NULLIF(%(orcid_id)s, ''),
                NULLIF(%(image)s, ''),
                %(config_class)s)
        RETURNING id
        """, {
            'email': data.get('email'),
            'website': data.get('website'),
            'orcid_id': data.get('orcid_id'),
            'image': data.get('image'),
            'config_class': config_class})
    id_ = g.cursor.fetchone()[0]
    _upsert_jsonb_fields(id_, data)

    return id_


def update_config_entry(data: dict) -> None:
    config_id = data['config_id']
    if not check_if_config_entry_exist(config_id):
        raise 404

    g.cursor.execute(
        """
        UPDATE tng.config
        SET email    = NULLIF(%(email)s, ''),
            website  = NULLIF(%(website)s, ''),
            orcid_id = NULLIF(%(orcid_id)s, ''),
            image    = NULLIF(%(image)s, '')
        WHERE id = %(config_id)s
        """,
        data)
    _upsert_jsonb_fields(config_id, data)


def _upsert_jsonb_fields(config_id: int, data: dict) -> None:
    language = g.language
    valid_cols = {'address', 'description', 'imprint', 'legal_notice', 'name'}
    for col in valid_cols:
        val = data.get(col, '')
        if val:
            g.cursor.execute(
                f"""
                UPDATE tng.config
                   SET {col} = jsonb_set(
                                 COALESCE({col}, '{{}}'),
                                 %(path)s,
                                 %(value)s::jsonb,
                                 true)
                 WHERE id = %(config_id)s
                """, {
                    'path': [language],
                    'value': json.dumps(val),
                    'config_id': config_id})
        else:
            g.cursor.execute(
                f"""
                UPDATE tng.config
                   SET {col} = COALESCE({col}, '{{}}') - %(key)s
                 WHERE id = %(config_id)s
                """, {
                    'key': language,
                    'config_id': config_id})


def check_sortorder() -> int:
    g.cursor.execute(
        '''
        SELECT COALESCE(MAX(sortorder) + 1, 1)
        FROM tng.links
        WHERE sortorder IS NOT NULL''')
    return g.cursor.fetchone()[0]


def add_link(data: dict[str, Any]) -> None:
    g.cursor.execute(
        '''
        INSERT INTO tng.links
        (domain_id, range_id, property, attribute, sortorder)
        VALUES (%(domain)s, %(range)s, %(prop)s, NULLIF(%(role)s, 0),
                %(sortorder)s)
        ''', {
            'domain': data['domain'],
            'range': data['range'],
            'prop': data['prop'],
            'role': data['role'],
            'sortorder': data['sortorder']})


def delete_link(id_: int) -> None:
    g.cursor.execute(
        """
        DELETE
        FROM tng.links
        WHERE id = %(link_id)s
        """, {
            'link_id': id_})
