from typing import Optional

import requests
from flask import g, jsonify, redirect, render_template, request, \
    session
from werkzeug import Response

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import ApiAccess
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


@cache.memoize()
def type_tree():
    response = requests.get(
        f"{app.config['API_URL']}/type_by_view_class/",
        headers=g.api_headers,
        timeout=20).json()
    return jsonify(response)


@app.route('/files_of_entities')
def files_of_entities() -> Response:
    return jsonify(ApiAccess.get_files_of_entities())
