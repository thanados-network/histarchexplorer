from typing import Optional

from flask import redirect, render_template, request, session
from werkzeug import Response

from histarchexplorer import app
from histarchexplorer.database.map import get_map_tilestring
from histarchexplorer.database.settings import get_map_settings
from histarchexplorer.utils.cerberos import get_view_class_count


@app.route('/')
def index() -> str:
    map_data = get_map_settings()
    map_ = get_map_tilestring(map_data)

    view_classes = get_view_class_count()

    return render_template(
        'index.html',
        map=map_.tilestring,
        map_data=map_data,
        view_classes=view_classes)


@app.route('/search')
def search() -> str:
    return render_template('search.html')


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)
