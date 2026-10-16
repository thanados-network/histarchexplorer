import math
from typing import Any

from flask import (
    abort, g, jsonify, render_template, request, Response)

from histarchexplorer import app
from histarchexplorer.database import entities as db_entities
from histarchexplorer.views.views import type_tree


def _build_browse_filter(
        id_: int = 0,
        extra_classes: tuple[str, ...] | list[str] | None = None) -> tuple[
            str, list[Any], dict[str, Any]] | None:
    """Build where clause, parameters, and settings for entity browsing."""
    shown_ids = g.settings.shown_ids

    if id_:
        # Get p46 children if id is provided
        shown_ids = db_entities.get_p46_range_ids(id_)
        if not shown_ids:
            return None

    data: dict[str, Any] = {
        'shown classes': g.settings.shown_classes,
        'hidden classes': g.settings.hidden_classes,
        'shown types': db_entities.build_id_collection(
            g.settings.shown_types),
        'hidden types': db_entities.build_id_collection(
            g.settings.hidden_types),
        'shown case studies': g.case_study_ids,
        'shown ids': shown_ids,
        'hidden ids': g.settings.hidden_ids}
    where_clauses: list[str] = []
    params: list[Any] = []

    if extra_classes is not None:
        effective_classes = [
            c for c in extra_classes
            if (not data['shown classes'] or c in data['shown classes'])
            and (not data['hidden classes']
                 or c not in data['hidden classes'])]
        where_clauses.append("e.openatlas_class_name = ANY (%s)")
        params.append(list(effective_classes))
    else:
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
            "WHERE b.property_code = 'P2' AND b.range_id = ANY (%s))")
        params.append(shown_types)

    if shown_case_studies := data['shown case studies']:
        where_clauses.append(
            "e.id IN (SELECT a.id FROM model.entity a "
            "JOIN model.link b ON a.id = b.domain_id "
            "WHERE b.property_code = 'P2' AND b.range_id = ANY (%s))")
        params.append(shown_case_studies)

    if hidden_types := data['hidden types']:
        where_clauses.append(
            "e.id NOT IN (SELECT a.id FROM model.entity a "
            "JOIN model.link b ON a.id = b.domain_id "
            "WHERE b.property_code = 'P2' AND b.range_id = ANY (%s))")
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

    return where_sql, params, data


def get_browse_metadata(
        id_: int = 0) -> dict[str, Any] | None:
    """Compile counts and browsing metadata without fetching entities.

    Executes class counts and case study queries in under 20ms, producing
    the categorized totals and filter structures needed by the page shell.
    """
    filter_res = _build_browse_filter(id_)
    if filter_res is None:
        return None
    where_sql, params, data = filter_res

    results = db_entities.get_class_counts(where_sql, tuple(params))
    class_count_map = {
        row['openatlas_class_name']: row['count'] for row in results}

    categorized_counts = {}
    for category, class_names in app.config['VIEW_CLASSES'].items():
        category_counts = [
            {cls: class_count_map[cls]}
            for cls in class_names if cls in class_count_map]
        if category_counts:
            categorized_counts[category] = category_counts

    category_totals = {
        category: sum(next(iter(d.values())) for d in items)
        for category, items in categorized_counts.items()}

    data['cs_ids'] = []
    if shown_case_studies := data['shown case studies']:
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


def get_browse_list_entities(
        id_: int = 0) -> dict[str, Any] | None:
    """Compile a list of entities and their geometries for browsing.

    Processes visible/hidden classes, types, and case studies to construct
    SQL conditions, fetches entities and geometries from the database,
    and returns categorized entity and count metadata.
    """
    data = get_browse_metadata(id_)
    if data is None:
        return None

    filter_res = _build_browse_filter(id_)
    if filter_res is None:
        return None
    where_sql, params, _ = filter_res

    data['entities'] = db_entities.get_entities_list(
        where_sql, tuple(params))
    data['geometries'] = db_entities.get_geometries(
        where_sql, tuple(params))
    return data


def get_browse_tab_data(
        tab_name: str,
        id_: int = 0,
        limit: int | None = None) -> dict[str, Any]:
    """Fetch entity and geometry records restricted to a single browse tab.

    Instead of fetching all 64,000+ entities across all categories, this
    loads only the entities belonging to the requested tab category.
    When limit is specified, it returns a fast lightweight page 1 payload
    accompanied by category metadata and distinct timeline dates.
    """
    class_names = app.config['VIEW_CLASSES'].get(tab_name, ())
    filter_res = _build_browse_filter(id_, extra_classes=class_names)
    if filter_res is None:
        return {
            'entities': [],
            'geometries': {'type': 'FeatureCollection', 'features': []},
            'cs_ids': [],
            'classes': [],
            'fields': [],
            'distinct_begins': [],
            'distinct_ends': [],
            'total': 0}

    where_sql, params, data = filter_res

    # Geometries are only used by tabs with map views (places, items)
    if tab_name in ('places', 'items'):
        geometries = db_entities.get_geometries(where_sql, tuple(params))
    else:
        geometries = {'type': 'FeatureCollection', 'features': []}

    cs_ids = []
    if shown_case_studies := data['shown case studies']:
        cs_infos = db_entities.get_case_study_infos(
            g.language, g.settings.preferred_language)
        matching_cs = db_entities.get_matching_case_study_ids(
            where_sql, tuple(params), shown_case_studies)
        for cs_id in matching_cs:
            row = next(
                (r for r in cs_infos if r['cs_id'] == cs_id), None)
            cs: dict[str, Any] = {'id': cs_id, 'ids': []}
            if row:
                if row['name']:
                    cs['name'] = row['name']
                    cs['acronym'] = row['name']
                if row['acronym']:
                    cs['acronym'] = row['acronym']
                if row['description']:
                    cs['description'] = row['description']
            cs_ids.append(cs)

    # Active classes for this tab
    class_counts = db_entities.get_class_counts(where_sql, tuple(params))
    classes = [
        row['openatlas_class_name'] for row in class_counts
        if row['count'] > 0]
    total_count = sum(row['count'] for row in class_counts)

    # Fields supported for this tab category
    if tab_name in ('places', 'items', 'features'):
        fields = [
            'id', 'name', 'description', 'class', 'type', 'begin', 'end']
    elif tab_name in ('actors', 'events'):
        fields = ['id', 'name', 'description', 'class', 'begin', 'end']
    else:
        fields = ['id', 'name', 'description', 'class']

    # Distinct dates for timeline sliders
    if 'begin' in fields or 'end' in fields:
        begins, ends = db_entities.get_distinct_dates(
            where_sql, tuple(params))
    else:
        begins, ends = [], []

    if limit is not None:
        entities, _ = db_entities.get_entities_page(
            where_sql, tuple(params), limit=limit, offset=0)
    else:
        entities = db_entities.get_entities_list(where_sql, tuple(params))

    return {
        'entities': entities,
        'geometries': geometries,
        'cs_ids': cs_ids,
        'classes': classes,
        'fields': fields,
        'distinct_begins': begins,
        'distinct_ends': ends,
        'total': total_count}


def return_entities(tab_name: str | None, id_: int | None) -> str:
    """Helper function to load entities and render the browsing layout.

    Retrieves browsing metadata, configures sidebar tabs with updated
    item counts, and renders the central entity template.
    """
    metadata = get_browse_metadata(id_ or 0)
    if not metadata:
        abort(404)

    filtered_view_classes = {
        key: tuple(list(d.keys())[0] for d in value)
        for key, value in metadata['counts'].items()}

    sidebar_elements = [
        {
            'order': i + 1,
            'route': key,
            'label': f"{key.capitalize()} ({metadata['totals'][key]})"}
        for i, key in enumerate(metadata['counts'].keys())]

    if not tab_name and sidebar_elements:
        tab_name = sidebar_elements[0]['route']

    frame_data = {
        'totals': metadata['totals'],
        'counts': metadata['counts']}

    return render_template(
        'entity.html',
        filtered_view_classes=filtered_view_classes,
        data=frame_data,
        sidebar_elements=sidebar_elements,
        entity_id=id_ or 0,
        page_name="landing",
        active_tab=tab_name,
        typetree_data={})


@app.route('/entities')
@app.route('/entities/<tab_name>')
@app.route('/entities/<tab_name>/<int:id_>')
def entities(tab_name: str | None = None, id_: int | None = None) -> str:
    """Render the main entity browse page.

    Handles routing for the entities list, allowing optional filtering by
    tab name or a specific parent entity ID.
    """
    return return_entities(tab_name, id_)


@app.route('/api/browse/<tab_name>')
def api_browse_tab(tab_name: str) -> Response:
    """Return paginated entity records formatted for remote Tabulator.

    Accepts page, size, sorting, fulltext query, and optional filter
    parameters (classes, types, entity IDs, parent entity ID).
    """
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)
    if page < 1:
        page = 1
    if size < 1:
        size = 50
    elif size > 200:
        size = 200

    sort_field = request.args.get('sort_field')
    sort_dir = request.args.get('sort_dir', 'asc')
    search_term = request.args.get('query', '').strip() or None
    id_ = request.args.get('id', 0, type=int)

    classes_param = request.args.get('classes', '').strip()
    if classes_param:
        target_classes = [
            c.strip() for c in classes_param.split(',') if c.strip()]
    else:
        target_classes = list(app.config['VIEW_CLASSES'].get(tab_name, ()))

    filter_res = _build_browse_filter(id_, extra_classes=target_classes)
    if filter_res is None:
        return jsonify({'data': [], 'total': 0, 'last_page': 1})

    where_sql, params, _ = filter_res
    effective_params: list[Any] = list(params)
    effective_clauses: list[str] = []

    types_param = request.args.get('types', '').strip()
    if types_param:
        type_ids = [
            int(t) for t in types_param.split(',')
            if t.strip().lstrip('-').isdigit()]
        if type_ids:
            effective_clauses.append(
                "e.id IN (SELECT a.id FROM model.entity a "
                "JOIN model.link b ON a.id = b.domain_id "
                "WHERE b.property_code = 'P2' AND b.range_id = ANY (%s))")
            effective_params.append(type_ids)

    entity_ids_param = request.args.get('entity_ids', '').strip()
    if entity_ids_param:
        ent_ids = [
            int(i) for i in entity_ids_param.split(',')
            if i.strip().lstrip('-').isdigit()]
        if ent_ids:
            effective_clauses.append("e.id = ANY (%s)")
            effective_params.append(ent_ids)

    if effective_clauses:
        extra_sql = " AND ".join(effective_clauses)
        if where_sql:
            where_sql = f"{where_sql} AND {extra_sql}"
        else:
            where_sql = f"WHERE {extra_sql}"

    offset = (page - 1) * size
    entities, total_count = db_entities.get_entities_page(
        where_sql,
        tuple(effective_params),
        limit=size,
        offset=offset,
        sort_field=sort_field,
        sort_dir=sort_dir,
        search_term=search_term)

    last_page = max(1, math.ceil(total_count / size))
    return jsonify({
        'data': entities,
        'total': total_count,
        'last_page': last_page})


@app.route('/get_entities/<tab_name>')
def get_entities(tab_name: str) -> str:
    """Render the partial tab template for AJAX loading of browse results.

    Returns the HTML segment corresponding to the specified browse tab.
    """
    tab_data = get_browse_tab_data(tab_name, limit=50)
    tab_classes = app.config['VIEW_CLASSES'].get(tab_name, ())
    full_tree = type_tree().get_json()
    tab_tree = {
        cls: full_tree[cls]
        for cls in tab_classes if cls in full_tree}
    return render_template(
        'tabs/browse.html',
        tab_name=tab_name,
        tab_data=tab_data,
        typetree_data=tab_tree)
