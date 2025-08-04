import json
from typing import Any, NamedTuple

from flask import g

from histarchexplorer.database.config import check_if_config_entry_exist


def get_config_links() -> Any:
    g.cursor.execute(
        """
        SELECT l.id        AS link_id,
               l.sortorder AS sortorder,
               s.id        AS start_id,
               s.name      AS start_name,
               cp.name     AS config_property,
               cp.id       AS property_id,
               'direct'    AS direction,
               e.name      AS end_name,
               e.id        AS end_id,
               r.name      AS role,
               r.id        AS role_id
        FROM tng.links l
                 JOIN tng.entities s ON l.domain_id = s.id
                 JOIN tng.entities e ON l.range_id = e.id
                 JOIN tng.properties cp ON l.property = cp.id
                 LEFT JOIN tng.entities r ON l.attribute = r.id
        UNION ALL
        SELECT l.id        AS link_id,
               l.sortorder AS sortorder,
               s.id        AS start_id,
               s.name      AS start_name,
               cp.name_inv AS config_property,
               cp.id       AS property_id,
               'inverse'   AS direction,
               e.name      AS end_name,
               e.id        AS end_id,
               r.name      AS role,
               r.id        AS role_id
        FROM tng.links l
                 JOIN tng.entities s ON l.range_id = s.id
                 JOIN tng.entities e ON l.domain_id = e.id
                 JOIN tng.properties cp ON l.property = cp.id
                 LEFT JOIN tng.entities r ON l.attribute = r.id
        ORDER BY sortorder
        """)
    return g.cursor.fetchall()


def get_config_properties() -> Any:
    g.cursor.execute(
        '''
        SELECT id, name, domain_type_id, range_type_id, 'direct' AS direction
        FROM tng.properties
        UNION ALL
        SELECT id,
               name_inv,
               range_type_id,
               domain_type_id,
               'inverse' AS direction
        FROM tng.properties''')
    return g.cursor.fetchall()


def get_config_class_by_id(id_: int) -> int | None:
    g.cursor.execute(
        'SELECT class_id FROM tng.entities WHERE id = %s',
        (id_,))
    row = g.cursor.fetchone()
    return row[0] if row else None


def set_hidden_classes(entities: list[str]) -> None:
    g.cursor.execute(
        'UPDATE tng.settings SET hidden_classes = %s',
        (entities,))


def set_shown_classes(entities: list[str]) -> None:
    g.cursor.execute(
        'UPDATE tng.settings SET shown_classes = %s',
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
    g.cursor.execute(
        "SELECT 1 FROM tng.entities WHERE class_id = 5 LIMIT 1")
    return g.cursor.fetchone() is not None


def delete_entry(id_: int) -> None:
    g.cursor.execute(
        'DELETE FROM tng.entities WHERE id = %(id)s',
        {'id': id_})


def add_entry(data: dict) -> int:
    config_class = g.config_classes_map.get(data['category'])
    if config_class is None:
        raise ValueError(f"Unknown category {data['category']}")
    if config_class == 5 and check_if_main_project_exist():
        raise 404
    g.cursor.execute(
        """
        INSERT INTO tng.entities
            (email, website, orcid_id, image, case_study_type_id, class_id)
        VALUES (NULLIF(%(email)s, ''),
                NULLIF(%(website)s, ''),
                NULLIF(%(orcid_id)s, ''),
                NULLIF(%(image)s, ''),
                NULLIF(%(case_study)s, NULL),
                %(class_id)s)
        RETURNING id
        """, {
            'email': data.get('email'),
            'website': data.get('website'),
            'orcid_id': data.get('orcid_id'),
            'image': data.get('image'),
            'case_study':  data.get('case_study'),
            'class_id': config_class})

    id_ = g.cursor.fetchone()[0]
    _upsert_jsonb_fields(id_, data)

    return id_


def update_config_entry(data: dict) -> None:
    config_id = data['config_id']
    if not check_if_config_entry_exist(config_id):
        raise 404

    g.cursor.execute(
        """
        UPDATE tng.entities
        SET email    = NULLIF(%(email)s, ''),
            website  = NULLIF(%(website)s, ''),
            orcid_id = NULLIF(%(orcid_id)s, ''),
            image    = NULLIF(%(image)s, ''),
            case_study_type_id = %(case_study)s
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
                UPDATE tng.entities
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
                UPDATE tng.entities
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


def get_openatlas_entity(id_) -> NamedTuple:
    g.cursor.execute(
        '''
        SELECT id, name, openatlas_class_name FROM model.entity
        WHERE id = %(id)s''', {'id': id_})
    return g.cursor.fetchone()

def update_case_study_type_hierarchy(id_: int) -> None:
    g.cursor.execute(
        'UPDATE tng.settings SET case_study_type_id = %s',
        (id_,))

def add_link(data: dict[str, Any]) -> None:
    g.cursor.execute(
        '''
        INSERT INTO tng.links
        (domain_id, range_id, property, attribute, sortorder)
        VALUES (%(domain)s, %(range)s, %(prop)s, NULLIF(%(attribute)s, 0),
                %(sortorder)s)
        ''', {
            'domain': data['domain'],
            'range': data['range'],
            'prop': data['prop'],
            'attribute': data['role'],
            'sortorder': data['sortorder']})


def delete_link(id_: int) -> None:
    g.cursor.execute(
        """
        DELETE
        FROM tng.links
        WHERE id = %(link_id)s
        """, {
            'link_id': id_})
