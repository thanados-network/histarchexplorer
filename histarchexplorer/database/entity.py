from typing import Any

from flask import g


def check_geom(id_: int) -> int | None:
    """Checks if an ID has geometry in model.gis via a linked entity."""
    g.openatlas_cursor.execute(
        """
        SELECT EXISTS
                   (SELECT 1
                    FROM model.gis
                    WHERE entity_id = (SELECT range_id
                                       FROM model.link
                                       WHERE domain_id = %(id)s
                                         AND property_code = 'P53'
                                       LIMIT 1)); \
        """, {'id': id_})
    result = g.openatlas_cursor.fetchone()
    return id_ if result and result['exists'] else None


def get_first_geom(id_: int) -> int | None:
    """Recursively finds the first entity with geometry."""
    id_to_return = check_geom(id_)
    if id_to_return:
        return id_to_return

    # Try to find the parent entity (domain_id)
    sql = """SELECT domain_id
             FROM model.link
             WHERE range_id = %(id)s
               AND property_code = 'P46'
             LIMIT 1; \
          """
    g.openatlas_cursor.execute(sql, {'id': id_})
    result = g.openatlas_cursor.fetchone()

    if result:
        parent_id = result['domain_id']
        return get_first_geom(parent_id)  # Recursively check the parent
    return None  # No parent found with geometry


def check_if_place_hierarchy(id_: int) -> bool:
    g.openatlas_cursor.execute(
        """
        SELECT range_id
        FROM model.link
        WHERE domain_id = %(id)s
          AND property_code = 'P46'
        LIMIT 1
        """, {"id": id_})
    return g.openatlas_cursor.fetchone() is not None


def get_files_for_ids(
        ids: list[int]) -> dict[str, list[dict[str, Any]]] | None:
    sql = """
          SELECT JSONB_AGG(
                         jsonb_build_object(
                                 'id', a.id,
                                 'name', a.name,
                                 'description', a.description,
                                 'bbox', a.bounding_box::JSONB
                         )
                 ) AS images
          FROM (SELECT e.id,
                       e.name,
                       e.description,
                       o.image_id,
                       o.bounding_box
                FROM model.entity e
                         JOIN model.link l ON e.id = l.domain_id
                         JOIN web.map_overlay o ON o.image_id = e.id
                WHERE e.openatlas_class_name = 'file'
                  AND l.range_id = ANY(%(ids)s)
                  AND l.property_code = 'P67') a;
          """
    g.openatlas_cursor.execute(sql, {'ids': ids})
    result = g.openatlas_cursor.fetchone()
    if result:
        return dict(result)
    return None
