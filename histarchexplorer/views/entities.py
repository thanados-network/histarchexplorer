from typing import Any

from flask import g, render_template

from histarchexplorer import app
from histarchexplorer.database import entities as db_entities
from histarchexplorer.views.views import type_tree


# pylint: disable=too-many-locals
def get_browse_list_entities(
        id_: int) -> dict[str, str | int | list[Any] | dict[str, Any]] | None:

    # per default the whitelist ids are shown
    shown_ids = g.settings.shown_ids

    # if an id is given the p46 children are requested
    # (Possible future dev: define another param - property code -
    # to get other connections to be shown)
    if id_:
        shown_ids = db_entities.get_p46_range_ids(id_)
        if not shown_ids:
            return None

    data = {
        'shown classes': g.settings.shown_classes,
        'hidden classes': g.settings.hidden_classes,
        'shown types': db_entities.build_id_collection(
            g.settings.shown_types),
        'hidden types': db_entities.build_id_collection(
            g.settings.hidden_types),
        'shown case studies': g.case_study_ids,
        'shown ids': shown_ids,
        'hidden ids': g.settings.hidden_ids}

    # Build WHERE clauses dynamically
    where_clauses = []
    params = []

    if shown_classes := data['shown classes']:
        where_clauses.append("e.openatlas_class_name = ANY (%s)")
        params.append(shown_classes)

    if hidden_classes := data['hidden classes']:
        where_clauses.append("e.openatlas_class_name != ALL (%s)")
        params.append(hidden_classes)

    if shown_types := data['shown types']:
        where_clauses.append(
            "e.id IN (SELECT a.id FROM model.entity a "
            "JOIN model.link b ON a.id = b.domain_id "
            "WHERE b.property_code = 'P2' AND b.range_id = ANY (%s))"
        )
        params.append(shown_types)

    if shown_case_studies := data['shown case studies']:
        where_clauses.append(
            "e.id IN (SELECT a.id FROM model.entity a "
            "JOIN model.link b ON a.id = b.domain_id "
            "WHERE b.property_code = 'P2' AND b.range_id = ANY (%s))"
        )
        params.append(shown_case_studies)

    if hidden_types := data['hidden types']:
        where_clauses.append(
            "e.id NOT IN (SELECT a.id FROM model.entity a "
            "JOIN model.link b ON a.id = b.domain_id "
            "WHERE b.property_code = 'P2' AND b.range_id = ANY (%s))"
        )
        params.append(hidden_types)

    if shown_ids_data := data['shown ids']:
        where_clauses.append("e.id = ANY (%s)")
        params.append(shown_ids_data)

    if hidden_ids := data['hidden ids']:
        where_clauses.append("e.id != ALL (%s)")
        params.append(hidden_ids)

    where_sql = " AND ".join(where_clauses)
    if where_sql:
        where_sql = "WHERE " + where_sql

    data['entities'] = db_entities.get_entities_list(
        where_sql, tuple(params))
    data['geometries'] = db_entities.get_geometries(
        where_sql, tuple(params))

    results = db_entities.get_class_counts(where_sql, tuple(params))

    # Convert list of (class_name, count) to a dictionary for easy access
    class_count_map = {
        row['openatlas_class_name']: row['count'] for row in results
    }

    # Build categorized counts
    categorized_counts = {}
    for category, class_names in app.config['VIEW_CLASSES'].items():
        category_counts = [
            {cls: class_count_map[cls]}
            for cls in class_names if cls in class_count_map
        ]
        if category_counts:  # Only include non-empty categories
            categorized_counts[category] = category_counts

    category_totals = {
        category: sum(next(iter(d.values())) for d in items)
        for category, items in categorized_counts.items()
    }

    data['cs_ids'] = []
    # build id lists for case studies
    if shown_case_studies:
        cs_infos = db_entities.get_case_study_infos(
            g.language, g.settings.preferred_language)

        for case_study in shown_case_studies:
            ids = db_entities.get_case_study_ids(case_study)
            if ids:
                cs = {'id': case_study, 'ids': ids}
                for row in cs_infos:
                    if row['cs_id'] == cs['id']:
                        if row['name']:
                            cs['name'] = row['name']
                            cs['acronym'] = row['name']
                        if row['acronym']:
                            cs['acronym'] = row['acronym']
                        if row['description']:
                            cs['description'] = row['description']
                data['cs_ids'].append(cs)

    data['totals'] = category_totals
    data['counts'] = categorized_counts
    return data


# get entities and return the template
def return_entities(tab_name: str, id_: int) -> str:
    data = get_browse_list_entities(id_)

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

    if not tab_name and sidebar_elements:
        tab_name = sidebar_elements[0]['route']

    return render_template(
        'entity.html',
        filtered_view_classes=filtered_view_classes,
        data=data,
        sidebar_elements=sidebar_elements,
        entity_id=0,
        page_name="landing",
        active_tab=tab_name,
        typetree_data=type_tree().json)


@app.route('/entities')
@app.route('/entities/<tab_name>')
@app.route('/entities/<tab_name>/<int:id_>')
def entities(tab_name: str | None = None, id_: int | None = None) -> str:
    return return_entities(tab_name, id_)


@app.route('/get_entities/<tab_name>')
def get_entities(tab_name: str) -> str:
    return render_template(
        'tabs/browse.html',
        tab_name=tab_name)
