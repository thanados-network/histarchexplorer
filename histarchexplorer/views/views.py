from typing import Optional

import requests
from flask import (
    g, jsonify, redirect, render_template, request, session, url_for)
from flask_login import login_required
from werkzeug import Response

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import ApiAccess, \
    get_entities_count_by_case_study
from histarchexplorer.api.presentation_view import PresentationView
from histarchexplorer.database.map import get_map_tilestring
from histarchexplorer.utils.cerberos import get_view_class_count


@app.route('/')
def index() -> str:
    map_data = g.settings.get_map_settings()
    map_ = None
    if index_map := map_data['map']:
        map_ = get_map_tilestring(index_map).tilestring
    view_classes = get_view_class_count()
    return render_template(
        'index.html',
        map=map_,
        map_data=map_data,
        view_classes=view_classes)


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)


@app.route('/type-tree')
def type_tree():
    return jsonify(ApiAccess.get_type_tree())

@app.route('/type-tree-overview')
def type_tree_overview():
    return jsonify(ApiAccess.get_type_tree_overview())


@app.route('/files-of-entities')
def get_files_of_entities():
    return jsonify(ApiAccess.get_files_of_entities())

@app.route('/entities-count')
def get_entities_count_by_case_study():
    return jsonify(get_entities_count_by_case_study())




@app.route("/refresh-cache/<int:id_>", methods=["POST"])
@login_required
def refresh_cache(id_: int):
    """Clear memoized cache for this entity."""
    try:
        cache.delete_memoized(PresentationView.from_api, PresentationView, id_)
        return redirect(url_for('entity_view', id_=id_))
    except Exception as e:
        return jsonify({"message": f"Failed to clear cache: {e}"}), 500
