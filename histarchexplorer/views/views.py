from typing import Optional

from flask import (
    Response, g, jsonify, redirect, render_template, request, session, url_for)
from flask.typing import ResponseValue
from flask_login import login_required

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.api.presentation_view import PresentationView
from histarchexplorer.database.map import get_map_tilestring
from histarchexplorer.models.config import ConfigEntity
from histarchexplorer.utils.view_util import get_view_class_count, slugify


def register_individual_pages(app):
    for page in app.config['INDIVIDUAL_PAGES']:
        if page in ('index', 'about'):
            continue

        def make_view(page_name):
            def view():
                return render_template(
                    "individual/content.html",
                    content=page_name
                )
            return view

        app.add_url_rule(
            f"/{page}",
            endpoint=f"individual_{page}",
            view_func=make_view(page)
        )
register_individual_pages(app)

@app.route('/')
def index() -> str:
    if 'index' in app.config['INDIVIDUAL_PAGES']:
        return render_template("individual/content.html", content="index")
    # todo: replace g.settings.get_map_settings()  with g.settings
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
def set_language(language: Optional[str] = None) -> ResponseValue:
    session['language'] = language
    return redirect(request.referrer)


@app.route('/type-tree')
def type_tree() -> Response:
    return jsonify(ApiAccess.get_type_tree())


@app.route('/files-of-entities')
def get_files_of_entities() -> Response:
    return jsonify(ApiAccess.get_files_of_entities())


@app.route('/entities-count')
def get_entities_count_by_case_study() -> Response:
    return jsonify(ApiAccess.get_entities_count_by_case_studies())


@app.route("/refresh-cache/<int:id_>", methods=["GET", "POST"])
@login_required
def refresh_cache(id_: int) -> ResponseValue | tuple[ResponseValue, int]:
    try:
        cache.delete_memoized(PresentationView.from_api, PresentationView, id_)
        return redirect(url_for('entity_view', id_=id_))
    except Exception as e:
        return jsonify({"message": f"Failed to clear cache: {e}"}), 500
