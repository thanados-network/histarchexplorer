from typing import Optional

from flask import (
    g, jsonify, redirect, render_template, request, session, url_for)
from flask_login import login_required
from werkzeug import Response

from histarchexplorer import ConfigEntity, app, cache
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.api.presentation_view import PresentationView
from histarchexplorer.database.map import get_map_tilestring
from histarchexplorer.utils.view_util import get_view_class_count, slugify


@app.route('/')
def index() -> str:
    map_data = g.settings.get_map_settings()
    map_ = None
    if index_map := map_data['map']:
        map_ = get_map_tilestring(index_map).tilestring

    grouped = ConfigEntity.group_by_class_name(g.config_entities)
    main_project = grouped.get('main-project', [None])[0]
    sub_projects = grouped.get('project', [])

    projects = [main_project] + sub_projects if main_project else sub_projects

    project_cards = []
    for p in projects:
        slug = slugify(p.acronym)

        # ensure description is safe + truncated server-side
        desc_label = p.description.get("display", {}).get("label") \
            if p.description['display']['label'] else ""
        if desc_label:
            short_desc = desc_label[:200] + "…" if len(desc_label) > 120 \
                else desc_label
        else:
            short_desc = ""

        project_cards.append({
            "id": p.id,
            "name": p.name['display']['label'],
            "acronym": p.acronym,
            "slug": slug,
            "image": p.image,
            "description": short_desc})

    # This is just for the carousal
    project_cards = project_cards[:12]

    return render_template(
        'index.html',
        map=map_,
        map_data=map_data,
        view_class_count=get_view_class_count(),
        project_cards=project_cards)


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)


@app.route('/type-tree')
def type_tree():
    return jsonify(ApiAccess.get_type_tree())


@app.route('/files-of-entities')
def get_files_of_entities():
    return jsonify(ApiAccess.get_files_of_entities())


@app.route('/entities-count')
def get_entities_count_by_case_study():
    return jsonify(ApiAccess.get_entities_count_by_case_studies())


@app.route("/refresh-cache/<int:id_>", methods=["POST"])
@login_required
def refresh_cache(id_: int):
    """Clear memoized cache for this entity."""
    try:
        cache.delete_memoized(PresentationView.from_api, PresentationView, id_)
        return redirect(url_for('entity_view', id_=id_))
    except Exception as e:
        return jsonify({"message": f"Failed to clear cache: {e}"}), 500
