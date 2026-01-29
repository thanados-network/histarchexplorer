from flask import g


def check_geom(id_: int) -> int | None:
    """Checks if an ID has geometry in model.gis via a linked entity."""
    g.cursor.execute(
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
    result = g.cursor.fetchone()
    return id_ if result and result[0] else None


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
    g.cursor.execute(sql, {'id': id_})
    result = g.cursor.fetchone()

    if result:
        parent_id = result[0]
        return get_first_geom(parent_id)  # Recursively check the parent
    return None  # No parent found with geometry


def check_if_place_hierarchy(id_: int) -> int:
    g.cursor.execute(
        """
        SELECT range_id
        FROM model.link
        WHERE domain_id = %(id)s
          AND property_code = 'P46'
        LIMIT 1
        """, {"id": id_})
    return g.cursor.fetchone() is not None

# def get_entity_by_id(id_):
#     g.cursor.execute(
#         """
#         SELECT e.id,
#                e.cidoc_class_code,
#                e.name,
#                e.description,
#                e.created,
#                e.modified,
#                e.openatlas_class_name,
#                COALESCE(
#                        to_char(e.begin_from, 'yyyy-mm-dd hh24:mi:ss BC'), '')
#                    AS begin_from,
#                e.begin_comment,
#                COALESCE(to_char(e.begin_to, 'yyyy-mm-dd hh24:mi:ss BC'), '')
#                    AS begin_to,
#                COALESCE(to_char(e.end_from, 'yyyy-mm-dd hh24:mi:ss BC'), '')
#                    AS end_from,
#                e.end_comment,
#                COALESCE(to_char(e.end_to, 'yyyy-mm-dd hh24:mi:ss BC'), '')
#                    AS end_to
#         FROM model.entity e
#         WHERE e.id = %(id)s
#         GROUP BY e.id;
#         """, {'id': id_})
#     return g.cursor.fetchone()
