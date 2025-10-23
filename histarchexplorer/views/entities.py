from flask import g, render_template

from histarchexplorer import app
from histarchexplorer.views.views import type_tree_by_view


def get_recursive_type_ids(id):
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
    g.cursor.execute(sql, {'id': id})
    result = g.cursor.fetchall()
    #print('result get_recursive_type_ids(id)')
    #print(result)
    return result


def build_id_collection(ids):
    if not ids:
        return []

    result = [
        row[0]
        for id in ids
        for row in get_recursive_type_ids(id)
    ]
    #print('result build_id_collection(ids)')
    #print(result)
    return result


def get_browse_list_entities(id=None):

    #per default the whitelist ids are shown
    shown_ids = g.settings.shown_ids

    #if an id is given the p46 children are requested (Possible future dev: define another param - property code - to get other connections to be shown)
    if id:
        sql = """
        SELECT range_id from model.link where property_code = 'P46'  AND domain_id = %(id)s
        """
        g.cursor.execute(sql, {'id': id})
        shown_ids = g.cursor.fetchall()
        if not shown_ids:
            return None

    data = {
        'shown classes': g.settings.shown_classes,
        'hidden classes': g.settings.hidden_classes,
        'shown types': build_id_collection(g.settings.shown_types),
        'hidden types': build_id_collection(g.settings.hidden_types),
        'shown case studies':  g.case_study_ids,
        'shown ids': shown_ids,
        'hidden ids': g.settings.hidden_ids}

    # Build WHERE clauses dynamically
    where_clauses = []
    params = []

    if shown_classes := data['shown classes']:
        where_clauses.append("e.openatlas_class_name = ANY (%s)")
        params.append(shown_classes)

    if hidden_classes:= data['hidden classes']:
        where_clauses.append("e.openatlas_class_name != ALL (%s)")
        params.append(hidden_classes)

    if shown_types:= data['shown types']:
        where_clauses.append("e.id IN (SELECT a.id FROM model.entity a JOIN model.link b ON a.id = b.domain_id WHERE b.property_code = 'P2' AND b.range_id = ANY (%s))")
        params.append(shown_types)

    if shown_case_studies:= data['shown case studies']:
        where_clauses.append("e.id IN (SELECT a.id FROM model.entity a JOIN model.link b ON a.id = b.domain_id WHERE b.property_code = 'P2' AND b.range_id = ANY (%s))")
        params.append(shown_case_studies)

    if hidden_types:= data['hidden types']:
        where_clauses.append("e.id NOT IN (SELECT a.id FROM model.entity a JOIN model.link b ON a.id = b.domain_id WHERE b.property_code = 'P2' AND b.range_id = ANY (%s))")
        params.append(hidden_types)

    if shown_ids:= data['shown ids']:
        where_clauses.append("e.id = ANY (%s)")
        params.append(shown_ids)

    if hidden_ids:= data['hidden ids']:
        where_clauses.append("e.id != ALL (%s)")
        params.append(hidden_ids)

    where_sql = " AND ".join(where_clauses)
    if where_sql:
        where_sql = "WHERE " + where_sql

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
SELECT a.name, a.id, a.description, a.openatlas_class_name, ac.id AS typeid, c.name as type, tng.getdates(a.begin_from, a.begin_to, a.begin_comment) AS begin, tng.getdates(a.end_to, a.end_from, a.end_comment) AS end
FROM model.entity a JOIN model.link l1 ON l1.domain_id = a.id
JOIN all_children ac ON l1.range_id = ac.id JOIN model.entity c ON c.id = ac.id WHERE l1.property_code = 'P2' UNION ALL
SELECT a.name, a.id, a.description, a.openatlas_class_name, null AS typeid, null as type, tng.getdates(a.begin_from, a.begin_to, a.begin_comment) AS begin, tng.getdates(a.end_to, a.end_from, a.end_comment) AS end
FROM model.entity a WHERE id NOT IN (SELECT a.id
FROM model.entity a JOIN model.link l1 ON l1.domain_id = a.id
JOIN all_children ac ON l1.range_id = ac.id JOIN model.entity c ON c.id = ac.id WHERE l1.property_code = 'P2')) e {where_sql}
    """

    #print((query, tuple(params)))
    g.cursor.execute(query, tuple(params))
    data['entities'] = g.cursor.fetchone()[0] or []

    geom_query = f"""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(
            
                                COALESCE(g.geom_point, g.geom_polygon, g.geom_linestring), 4326
            
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

    g.cursor.execute(geom_query, tuple(params))
    data['geometries'] = g.cursor.fetchone()[0] or []

    count_query = f"""
                     SELECT e.openatlas_class_name, COUNT(*) AS count
                     FROM model.entity e
                     {where_sql}
                     GROUP BY e.openatlas_class_name
                     """

    g.cursor.execute(count_query, tuple(params))
    results = g.cursor.fetchall()

    # Convert list of (class_name, count) to a dictionary for easy access
    class_count_map = {row[0]: row[1] for row in results}

    # Build categorized counts
    categorized_counts = {}
    for category, class_names in app.config['VIEW_CLASSES'].items():
        category_counts = [
            {cls: class_count_map[cls]} for cls in class_names if cls in class_count_map
        ]
        if category_counts:  # Only include non-empty categories
            categorized_counts[category] = category_counts

    category_totals = {
        category: sum(next(iter(d.values())) for d in items)
        for category, items in categorized_counts.items()
    }

    data['cs_ids'] = []
    #build id lists for case studies
    if shown_case_studies:
        sql_get_cs_infos = """
        SELECT
            -- --- Name Extraction Logic (Three-Level Fallback) ---
            COALESCE(
                -- 1. Try the requested language (e.g., 'fr')
                t.name ->> %(language)s,
        
                -- 2. Try the preferred/fallback language (e.g., 'en')
                t.name ->> %(preferred_language)s,
        
                -- 3. Try any available language key (gets the value of the first key found)
                t.name ->> (SELECT key FROM jsonb_each(t.name) LIMIT 1)
            ) AS name,
        
            -- --- Description Extraction Logic (Three-Level Fallback) ---
            COALESCE(
                -- 1. Try the requested language (e.g., 'fr')
                t.description ->> %(language)s,
        
                -- 2. Try the preferred/fallback language (e.g., 'en')
                t.description ->> %(preferred_language)s,
        
                -- 3. Try any available language key
                t.description ->> (SELECT key FROM jsonb_each(t.description) LIMIT 1)
            ) AS description,
            t.case_study_type_id AS cs_id
        FROM
            tng.entities AS t
        WHERE
            t.case_study_type_id IS NOT NULL
        """

        g.cursor.execute(sql_get_cs_infos, {'language': g.language, 'preferred_language': app.config.get('PREFERRED_LANGUAGE')})
        cs_infos = g.cursor.fetchall()

        sql_case_studies = """
            SELECT jsonb_agg(domain_id) as ids
            FROM model.link
            WHERE range_id = %(cs_id)s
              AND property_code = 'P2';
        """
        for case_study in shown_case_studies:
            g.cursor.execute(sql_case_studies, {'cs_id':case_study})
            results = g.cursor.fetchone()
            cs = {'id': case_study, 'ids': results}
            for row in cs_infos:
                if row.cs_id == cs['id']:
                    if row.name:
                        cs['name'] = row.name
                    if row.description:
                        cs['description'] = row.description
            data['cs_ids'].append(cs)



    data['totals'] = category_totals
    data['counts'] = categorized_counts
    return data


# get entities and return the template
def return_entities(tab_name, id):
    data = get_browse_list_entities(id)

    filtered_view_classes = {
        key: tuple(list(d.keys())[0] for d in value)
        for key, value in data['counts'].items()
    }

    sidebar_elements = [
        {
            'order': i + 1,
            'route': key,
            'label': f"{key.capitalize()} ({data['totals'][key]})"
        }
        for i, key in enumerate(data['counts'].keys())
    ]



    if tab_name == "" and sidebar_elements:
        tab_name = sidebar_elements[0]['route']

    return render_template(
        'entity.html',
        view_classes=filtered_view_classes,
        data=data,
        sidebar_elements=sidebar_elements,
        entity_id=0,
        page_name="landing",
        active_tab=tab_name,
        typetree_data=type_tree_by_view().json,
        main_image_json=g.main_images)


@app.route('/entities')
@app.route('/entities/<tab_name>')
@app.route('/entities/<tab_name>/<id>')
def entities(tab_name="", id=None) -> str:
    return return_entities(tab_name, id)




@app.route('/get_entities/<tab_name>')
def get_entities(tab_name: str) -> str:
    return render_template(
        f'tabs/browse.html',
        tab_name=tab_name)
