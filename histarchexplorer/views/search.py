"""Views and JSON endpoints for the OpenAtlas v1 search interface."""
from typing import Any

from flask import Response, g, jsonify, request
from flask_babel import gettext as _

from histarchexplorer import app
from histarchexplorer.models.search import OPENATLAS_SEARCH_CLASSES
from histarchexplorer.services.statistics import CLASS_KPI_META
from histarchexplorer.utils.view_util import render_page_template


def _get_available_case_studies() -> list[dict[str, Any]]:
    """Return configured case studies with localized project names."""
    case_studies: list[dict[str, Any]] = []
    seen: set[int] = set()
    for entity in getattr(g, 'config_entities', []) or []:
        cs_id = getattr(entity, 'case_study', None)
        if not cs_id or cs_id <= 0 or cs_id in seen:
            continue
        seen.add(int(cs_id))
        name_dict = getattr(entity, 'name', {}) or {}
        label = (
            name_dict.get('display', {}).get('label')
            or getattr(entity, 'acronym', '')
            or f'Case Study {cs_id}')
        acronym = getattr(entity, 'acronym', '') or label
        case_studies.append({
            'id': int(cs_id),
            'name': str(label),
            'acronym': str(acronym)})
    return case_studies


def _get_available_classes() -> tuple[
        list[dict[str, str]], dict[str, dict[str, str]]]:
    """Build available entity classes and a complete metadata lookup map."""
    shown_raw = (
        getattr(g.settings, 'shown_classes', None)
        if hasattr(g, 'settings') else None) or []
    hidden_raw = (
        getattr(g.settings, 'hidden_classes', None)
        if hasattr(g, 'settings') else None) or []
    shown_set = set(shown_raw)
    hidden_set = set(hidden_raw)
    if 'place' not in hidden_set:
        shown_set.add('place')

    available: list[dict[str, str]] = []
    meta_map: dict[str, dict[str, str]] = {}

    for cls_key, meta in CLASS_KPI_META.items():
        entry = {
            'key': cls_key,
            'label': str(meta['label']),
            'icon': meta['icon'],
            'color_key': meta['color_key'],
            'tab': meta['tab']}
        meta_map[cls_key] = entry
        if cls_key not in OPENATLAS_SEARCH_CLASSES:
            continue
        if shown_set and (cls_key not in shown_set or cls_key in hidden_set):
            continue
        available.append(entry)

    for extra_key in OPENATLAS_SEARCH_CLASSES:
        if extra_key not in meta_map:
            meta_map[extra_key] = {
                'key': extra_key,
                'label': _(extra_key.replace('_', ' ').title()),
                'icon': 'bi-tag',
                'color_key': 'types',
                'tab': 'places'}

    return available, meta_map


def _parse_int_list(values: list[str]) -> list[int] | None:
    """Parse a list of query string values into positive integers."""
    parsed = [
        int(val) for val in values
        if val and str(val).strip().isdigit() and int(val) > 0]
    return parsed if parsed else None


def _extract_search_params() -> dict[str, Any]:
    """Extract normalized search parameters from GET or POST request data."""
    source = request.form if request.method == 'POST' else request.args
    query = (
        source.get('search')
        or source.get('q')
        or source.get('query')
        or '').strip()
    entity_classes = [
        sc for sc in (
            source.getlist('entityClass')
            or source.getlist('system_class')
            or source.getlist('system_class[]'))
        if sc and sc != 'all']
    raw_cs = (
        source.getlist('caseStudy')
        or source.getlist('case_study'))
    case_study_ids = _parse_int_list(raw_cs)
    start_date = (
        source.get('startDate')
        or source.get('start_date')
        or '').strip() or None
    end_date = (
        source.get('endDate')
        or source.get('end_date')
        or '').strip() or None
    sort_by = (
        source.get('sortBy')
        or source.get('sort_by')
        or 'name').strip()
    sort_order = (
        source.get('sort')
        or source.get('sort_order')
        or 'asc').strip()

    raw_limit = source.get('limit', '50')
    limit = int(raw_limit) if str(raw_limit).isdigit() else 50
    raw_page = source.get('page', '1')
    page = int(raw_page) if str(raw_page).isdigit() else 1

    return {
        'query': query,
        'entity_classes': entity_classes,
        'case_study_ids': case_study_ids,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'limit': max(1, min(100, limit)),
        'page': max(1, page)}


@app.route('/search', methods=['GET', 'POST'])
def search() -> str:
    """Render the interactive OpenAtlas v1 search interface."""
    params = _extract_search_params()
    available_case_studies = _get_available_case_studies()
    available_classes, class_meta_map = _get_available_classes()

    return render_page_template(
        'search',
        available_case_studies=available_case_studies,
        available_classes=available_classes,
        class_meta_map=class_meta_map,
        initial_state=params)


@app.route('/api/search')
def api_search() -> Response:
    """Execute a full search against `/api/1/search` and return JSON."""
    params = _extract_search_params()
    payload = g.search_service.execute_search(
        query=params['query'],
        entity_classes=params['entity_classes'],
        case_study_ids=params['case_study_ids'],
        start_date=params['start_date'],
        end_date=params['end_date'],
        sort_by=params['sort_by'],
        sort_order=params['sort_order'],
        limit=params['limit'],
        page=params['page'])
    return jsonify(payload)


@app.route('/search_live')
def search_live() -> Response:
    """Return autocomplete live search results as a JSON list."""
    params = _extract_search_params()
    results = g.search_service.perform_live_search(
        params['query'],
        params['entity_classes'],
        case_study_ids=params['case_study_ids'])
    return jsonify(results)
