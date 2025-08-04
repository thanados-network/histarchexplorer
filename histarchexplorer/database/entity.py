# This is just a temporary solution, to make the some calls efficient until
#   a custom made API endpoint is ready
from flask import g


def get_entity_by_id(id_):
    g.cursor.execute(
        """SELECT
            e.id,
            e.cidoc_class_code,
            e.name,
            e.description,
            e.created,
            e.modified,
            e.openatlas_class_name,
            COALESCE(to_char(e.begin_from, 'yyyy-mm-dd hh24:mi:ss BC'), '')
                AS begin_from,
            e.begin_comment,
            COALESCE(to_char(e.begin_to, 'yyyy-mm-dd hh24:mi:ss BC'), '')
                AS begin_to,
            COALESCE(to_char(e.end_from, 'yyyy-mm-dd hh24:mi:ss BC'), '')
                AS end_from,
            e.end_comment,
            COALESCE(to_char(e.end_to, 'yyyy-mm-dd hh24:mi:ss BC'), '')
                AS end_to
           FROM model.entity e 
           WHERE e.id = %(id)s GROUP BY e.id;""",
    {'id': id_})
    return g.cursor.fetchone()
