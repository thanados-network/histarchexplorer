
from typing import Any

from flask import g


def get_recursive_type_ids(id_: int) -> list[dict[str, Any]]:
    sql = """
            (WITH RECURSIVE children_chain AS (
            -- Anchor: start with the given id as the root
            SELECT
                 %(id)s AS id,   -- your starting ID here
                0 AS level
            UNION ALL
            -- Recursive: find children where the domain_id = parent's id
            SELECT
                l.domain_id AS id,
                cc.level + 1
            FROM model.link l
            JOIN children_chain cc ON l.range_id = cc.id
            WHERE l.property_code = 'P127'
        )
        SELECT id
        FROM children_chain
        ORDER BY level, id)
    """
    g.openatlas_cursor.execute(sql, {'id': id_})
    return g.openatlas_cursor.fetchall()


def build_id_collection(ids: list[int]) -> list[str]:
    if not ids:
        return []

    return [
        row['id']
        for id_ in ids
        for row in get_recursive_type_ids(id_)
    ]


def get_p46_range_ids(id_: int) -> list[int]:
    sql = """
    SELECT range_id from model.link 
    WHERE property_code = 'P46'  AND domain_id = %(id)s
    """
    g.openatlas_cursor.execute(sql, {'id': id_})
    return [row['range_id'] for row in g.openatlas_cursor.fetchall()]


def get_entities_list(where_sql: str, params: tuple) -> list[dict[str, Any]]:
    query = f"""
        SELECT jsonb_agg(
            jsonb_build_object(
                'id', e.id,
                'name', e.name,
                'description', e.description,
                'class', e.openatlas_class_name,
                'type', e.type,
                'type_id', e.typeid,
                'begin', e.begin,
                'end', e.end
            )
        ) AS items
        FROM (WITH RECURSIVE all_children AS (
    SELECT h.id AS id
    FROM web.hierarchy h
    WHERE h.category = 'standard'

    UNION ALL

    SELECT l.domain_id
    FROM model.link l
    JOIN all_children ac ON l.range_id = ac.id
    WHERE l.property_code = 'P127'
)
SELECT a.name, a.id, a.description, a.openatlas_class_name, ac.id AS typeid,
       c.name as type,
       tng.getdates(a.begin_from, a.begin_to, a.begin_comment) AS begin,
       tng.getdates(a.end_to, a.end_from, a.end_comment) AS end
FROM model.entity a JOIN model.link l1 ON l1.domain_id = a.id
JOIN all_children ac ON l1.range_id = ac.id
JOIN model.entity c ON c.id = ac.id WHERE l1.property_code = 'P2' UNION ALL
SELECT a.name, a.id, a.description, a.openatlas_class_name, null AS typeid,
       null as type,
       tng.getdates(a.begin_from, a.begin_to, a.begin_comment) AS begin,
       tng.getdates(a.end_to, a.end_from, a.end_comment) AS end
FROM model.entity a WHERE id NOT IN (SELECT a.id
FROM model.entity a JOIN model.link l1 ON l1.domain_id = a.id
JOIN all_children ac ON l1.range_id = ac.id
JOIN model.entity c ON c.id = ac.id WHERE l1.property_code = 'P2')) e {where_sql}
    """
    g.openatlas_cursor.execute(query, params)
    result = g.openatlas_cursor.fetchone()
    return result.get('items', []) if result else []


def get_geometries(where_sql: str, params: tuple) -> dict[str, Any] | list:
    geom_query = f"""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(
                            COALESCE(
                                g.geom_point, g.geom_polygon, g.geom_linestring
                            ), 4326
                        )::jsonb,
                        'properties', jsonb_build_object(
                            'id', e.id,
                            'name', e.name,
                            'class', e.openatlas_class_name
                        )
                    )
                )
            ) AS geojson
            FROM model.entity e
            JOIN model.link l
                ON e.id = l.domain_id
            JOIN model.gis g
                ON g.entity_id = l.range_id
            {where_sql} 
            AND l.property_code = 'P53'
              AND (
                  g.geom_point IS NOT NULL
                  OR g.geom_polygon IS NOT NULL
                  OR g.geom_linestring IS NOT NULL
              );
"""
    g.openatlas_cursor.execute(geom_query, params)
    result = g.openatlas_cursor.fetchone()
    return result['geojson'] if result else []


def get_class_counts(where_sql: str, params: tuple) -> list[dict[str, Any]]:
    count_query = f"""
                     SELECT e.openatlas_class_name, COUNT(*) AS count
                     FROM model.entity e
                     {where_sql}
                     GROUP BY e.openatlas_class_name
                     """
    g.openatlas_cursor.execute(count_query, params)
    return g.openatlas_cursor.fetchall()


def get_case_study_infos(
        language: str,
        preferred_language: str) -> list[dict[str, Any]]:
    sql = """
    SELECT
        COALESCE(
            t.name ->> %(language)s,
            t.name ->> %(preferred_language)s,
            t.name ->> (SELECT key FROM jsonb_each(t.name) LIMIT 1)
        ) AS name,
        COALESCE(
            t.description ->> %(language)s,
            t.description ->> %(preferred_language)s,
            t.description ->> (SELECT key FROM jsonb_each(t.description) LIMIT 1)
        ) AS description,
        t.case_study_type_id AS cs_id,
        t.acronym AS acronym
    FROM
        tng.entities AS t
    WHERE
        t.case_study_type_id IS NOT NULL
    """
    g.cursor.execute(sql, {
        'language': language,
        'preferred_language': preferred_language})
    return g.cursor.fetchall()


def get_case_study_ids(cs_id: int) -> list[int]:
    sql = """
        SELECT array_agg(domain_id) as ids
        FROM model.link
        WHERE range_id = %(cs_id)s
          AND property_code = 'P2';
    """
    g.openatlas_cursor.execute(sql, {'cs_id': cs_id})
    results = g.openatlas_cursor.fetchone()
    return results['ids'] if results else []


def get_entities_page(
        where_sql: str,
        params: tuple,
        limit: int = 50,
        offset: int = 0,
        sort_field: str | None = None,
        sort_dir: str = 'asc',
        search_term: str | None = None) -> tuple[list[dict[str, Any]], int]:
    """Fetch a single paginated page of entities and total matching count.

    Uses an optimized 2-stage CTE to sort and paginate the entity records
    before joining standard type hierarchies, keeping query latencies low.
    """
    effective_params: list[Any] = list(params)
    effective_where_sql = where_sql

    if search_term:
        search_clause = "(e.name ILIKE %s OR e.description ILIKE %s)"
        like_term = f"%{search_term}%"
        effective_params.extend([like_term, like_term])
        if effective_where_sql:
            effective_where_sql = f"{effective_where_sql} AND {search_clause}"
        else:
            effective_where_sql = f"WHERE {search_clause}"

    count_sql = (
        f"SELECT count(*) AS total FROM model.entity e {effective_where_sql}")
    g.openatlas_cursor.execute(count_sql, tuple(effective_params))
    count_row = g.openatlas_cursor.fetchone()
    total_count = count_row['total'] if count_row else 0

    if total_count == 0 or limit <= 0:
        return [], total_count

    direction = 'DESC' if sort_dir and sort_dir.lower() == 'desc' else 'ASC'
    if sort_field == 'class':
        order_e = f"e.openatlas_class_name {direction}, e.name ASC"
        order_p = f"p.class {direction}, p.name ASC"
    elif sort_field == 'begin':
        order_e = f"e.begin_from {direction} NULLS LAST, e.name ASC"
        order_p = f"p.begin {direction} NULLS LAST, p.name ASC"
    elif sort_field == 'end':
        order_e = f"e.end_to {direction} NULLS LAST, e.name ASC"
        order_p = f"p.end {direction} NULLS LAST, p.name ASC"
    elif sort_field == 'id':
        order_e = f"e.id {direction}"
        order_p = f"p.id {direction}"
    else:
        order_e = f"e.name {direction}"
        order_p = f"p.name {direction}"

    query = f"""
        WITH RECURSIVE all_children AS (
            SELECT h.id AS id
            FROM web.hierarchy h
            WHERE h.category = 'standard'
            UNION ALL
            SELECT l.domain_id
            FROM model.link l
            JOIN all_children ac ON l.range_id = ac.id
            WHERE l.property_code = 'P127'
        ),
        page_entities AS (
            SELECT e.id, e.name, e.description,
                   e.openatlas_class_name AS class,
                   tng.getdates(
                       e.begin_from, e.begin_to, e.begin_comment) AS begin,
                   tng.getdates(
                       e.end_to, e.end_from, e.end_comment) AS end
            FROM model.entity e
            {effective_where_sql}
            ORDER BY {order_e}
            LIMIT %s OFFSET %s
        ),
        types AS (
            SELECT DISTINCT ON (l1.domain_id)
                   l1.domain_id, c.id AS type_id, c.name AS type
            FROM model.link l1
            JOIN all_children ac ON l1.range_id = ac.id
            JOIN model.entity c ON c.id = ac.id
            WHERE l1.property_code = 'P2'
              AND l1.domain_id IN (SELECT id FROM page_entities)
        )
        SELECT p.id, p.name, p.description, p.class,
               t.type, t.type_id, p.begin, p.end
        FROM page_entities p
        LEFT JOIN types t ON p.id = t.domain_id
        ORDER BY {order_p};
    """
    g.openatlas_cursor.execute(
        query, tuple(effective_params) + (limit, offset))
    rows = g.openatlas_cursor.fetchall()
    return [dict(r) for r in rows] if rows else [], total_count


def get_distinct_dates(
        where_sql: str,
        params: tuple) -> tuple[list[str], list[str]]:
    """Retrieve unique non-null begin and end dates for timeline sliders."""
    sql_begins = f"""
        SELECT DISTINCT tng.getdates(
            e.begin_from, e.begin_to, e.begin_comment) AS d
        FROM model.entity e {where_sql}
        AND e.begin_from IS NOT NULL
        ORDER BY d ASC
    """
    g.openatlas_cursor.execute(sql_begins, params)
    rows_begin = g.openatlas_cursor.fetchall()
    begins = [r['d'] for r in rows_begin if r.get('d')]

    sql_ends = f"""
        SELECT DISTINCT tng.getdates(
            e.end_to, e.end_from, e.end_comment) AS d
        FROM model.entity e {where_sql}
        AND e.end_to IS NOT NULL
        ORDER BY d ASC
    """
    g.openatlas_cursor.execute(sql_ends, params)
    rows_end = g.openatlas_cursor.fetchall()
    ends = [r['d'] for r in rows_end if r.get('d')]

    return begins, ends


def get_matching_case_study_ids(
        where_sql: str,
        params: tuple,
        case_study_ids: list[int]) -> list[int]:
    """Retrieve case study IDs that have entities matching the where clause."""
    if not case_study_ids:
        return []

    sql = f"""
        SELECT DISTINCT l.range_id
        FROM model.link l
        JOIN model.entity e ON l.domain_id = e.id
        {where_sql}
        AND l.property_code = 'P2'
        AND l.range_id = ANY (%s)
    """
    g.openatlas_cursor.execute(sql, tuple(params) + (case_study_ids,))
    rows = g.openatlas_cursor.fetchall()
    return [r['range_id'] for r in rows if r.get('range_id')]

