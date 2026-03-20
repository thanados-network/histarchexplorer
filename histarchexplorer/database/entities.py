
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
