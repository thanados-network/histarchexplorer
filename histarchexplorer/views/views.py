from typing import Optional

import requests
from flask import g, jsonify, redirect, render_template, abort, request, \
    session, current_app
from werkzeug import Response

from histarchexplorer import app, cache
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
        timeout=20).json()
    return jsonify(response)

@app.route("/vocabulary")
def vocabulary():
    type_filters = current_app.config.get("TYPE_FILTERS", {})
    return render_template("vocabulary.html", type_filters=type_filters)

from flask import render_template, current_app
import requests

@app.route("/vocabulary/<int:type_id>")
def vocabulary_detail(type_id):
    try:
        # Fetch full type tree
        res = requests.get("https://thanados.openatlas.eu/api/0.4/type_tree/")
        res.raise_for_status()
        type_tree = res.json().get("typeTree", {})

        # Get the type by ID
        this_type = type_tree.get(str(type_id))
        if not this_type:
            return f"Type with ID {type_id} not found.", 404

        # Resolve parents and children (as full objects)
        parents = [type_tree.get(str(pid)) for pid in this_type.get("root", [])]
        children = [type_tree.get(str(cid)) for cid in this_type.get("subs", [])]

        return render_template("vocabulary_detail.html",
                               this_type=this_type,
                               parents=parents,
                               children=children)
    except Exception as e:
        return f"Error loading type: {e}", 500

