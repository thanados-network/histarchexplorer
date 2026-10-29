import datetime
from typing import Optional

from flask import (
    Response, g, jsonify, redirect, request, session, url_for)
from flask.typing import ResponseValue
from flask_babel import gettext as _
from flask_login import login_required

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.database.map import get_map_tilestring
from histarchexplorer.models.config import ConfigEntity
from histarchexplorer.services.entity_cache import forget_entity
from histarchexplorer.services.statistics import (
    build_dynamic_landing_sections, get_landing_sites_geojson,
    get_landing_statistics)
from histarchexplorer.utils.view_util import (get_view_class_count,
                                              render_page_template, slugify)


@app.route('/')
def index() -> str:
    """Render the main landing page of the application.

    This function fetches map settings, builds project showcase
    cards, aggregates scientific statistics, and renders the index
    template.
    """
    map_data = g.settings.get_map_settings()
    map_ = None
    if index_map := map_data['map']:
        map_ = get_map_tilestring(index_map)

    grouped = ConfigEntity.group_by_class_name(g.config_entities)
    main_project = grouped.get('main-project', [None])[0]
    sub_projects = grouped.get('project', [])

    projects = [main_project] + sub_projects if main_project else sub_projects

    project_cards = []
    for p in projects:
        slug = slugify(p.acronym)

        desc_label = p.description.get("display", {}).get("label")
        if not desc_label:
            desc_label = ""

        if desc_label:
            short_desc = (
                desc_label[:200] + "…" if len(desc_label) > 120
                else desc_label)
        else:
            short_desc = ""

        project_cards.append({
            "id": p.id,
            "name": p.name['display']['label'],
            "acronym": p.acronym,
            "slug": slug,
            "image": p.image,
            "description": short_desc})

    # This is just for the carousel
    project_cards = project_cards[:12]

    case_study_tuple = tuple(g.case_study_ids)
    landing_stats = get_landing_statistics(case_study_tuple)
    view_class_count = get_view_class_count()
    kpi_cards, thematic_cards = build_dynamic_landing_sections(
        landing_stats, view_class_count)

    # Portal citation metadata
    current_year = datetime.datetime.now().year
    portal_name = "Histarchexplorer"
    if main_project and 'display' in main_project.name:
        portal_name = main_project.name['display'].get('label', portal_name)

    portal_url = request.url_root.rstrip('/')
    citation_apa = (
        f"{portal_name} ({current_year}). "
        f"Research Data Repository. {portal_url}")
    citation_bibtex = (
        f"@misc{{{slugify(portal_name)}_{current_year},\n"
        f"  title = {{{portal_name}}},\n"
        f"  year = {{{current_year}}},\n"
        f"  url = {{{portal_url}}}\n"
        f"}}")

    return render_page_template(
        'index',
        map=map_,
        map_data=map_data,
        view_class_count=view_class_count,
        kpi_cards=kpi_cards,
        thematic_cards=thematic_cards,
        project_cards=project_cards,
        main_project=main_project,
        landing_stats=landing_stats,
        citation_apa=citation_apa,
        citation_bibtex=citation_bibtex)


@app.route('/api/landing/sites-geojson')
def landing_sites_geojson() -> Response:
    """Return compact clustered sites GeoJSON for landing and about pages."""
    case_study_id = request.args.get('case_study', type=int)
    if case_study_id and case_study_id > 0:
        case_study_tuple = (case_study_id,)
    else:
        case_study_tuple = tuple(g.case_study_ids)
    data = get_landing_sites_geojson(case_study_tuple)
    return jsonify(data)


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> ResponseValue:
    """Update the user's preferred language in the session.

    Saves the selected language code to the session and redirects the
    user back to the previous page.
    """
    session['language'] = language
    return redirect(request.referrer)


@app.route('/type-tree')
def type_tree() -> Response:
    """Fetch and return the complete hierarchical type tree as JSON.

    Used by the frontend to build filter and selection menus based on
    available historical classifications.

    Returns:
        Response: JSON payload containing categories and type hierarchies
            as returned by `ApiAccess.get_type_tree`.
    """
    return jsonify(ApiAccess.get_type_tree())


@app.route('/files-of-entities')
def get_files_of_entities() -> Response:
    """Retrieve file information linked to all entities as JSON.

    This allows the frontend to query media associated with different
    archaeological and historical items.

    Returns:
        Response: JSON payload containing file mappings as returned by
            `ApiAccess.get_files_of_entities`.
    """
    return jsonify(ApiAccess.get_files_of_entities())


@app.route('/entities-count')
def get_entities_count_by_case_study() -> Response:
    """Get the number of entities within each case study as JSON.

    Provides count statistics to show how many items are registered
    under different projects or areas of study.

    Returns:
        Response: JSON payload containing class counts as returned by
            `ApiAccess.get_entities_count_by_case_studies`.
    """
    return jsonify(ApiAccess.get_entities_count_by_case_studies())


@app.route("/refresh-cache/<int:id_>", methods=["GET", "POST"])
@login_required
def refresh_cache(id_: int) -> ResponseValue | tuple[ResponseValue, int]:
    """Clear cached data for a specific entity and reload its view.

    Requires administrative login. Deletes the memoized cache for the
    given entity ID, then redirects to its presentation page.

    Args:
        id_: int - The unique entity ID to refresh.

    Returns:
        ResponseValue: Redirect to the entity page on success, or JSON
            error message with HTTP 500 on failure.
    """
    try:
        forget_entity(id_)
        return redirect(url_for('entity_view', id_=id_))
    except Exception as e:
        return jsonify({
            "message": _("Failed to clear cache: %(error)s", error=e)}), 500
