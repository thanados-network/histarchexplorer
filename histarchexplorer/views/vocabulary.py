from collections.abc import Callable
from typing import Any

import requests
from flask import g, jsonify, url_for
from werkzeug import Response

from histarchexplorer import app
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.utils.view_util import render_page_template


@app.route('/vocabulary')
def vocabulary() -> str:
    """Render the default widget or the configured individual template."""
    language = str(g.language)
    detail_url = url_for('vocabulary_detail', id_=1)
    return render_page_template(
        'vocabulary',
        widget_language=language if language in ('de', 'en') else 'en',
        detail_endpoint=detail_url.rsplit('/', 1)[0] + '/{id}')


def _proxy(fetch: Callable[[], dict[str, Any]]) -> Response | tuple:
    """Serve cached upstream JSON without leaking credentials or errors."""
    try:
        return jsonify(fetch())
    except requests.Timeout:
        return jsonify(error='Vocabulary service timed out.'), 504
    except requests.HTTPError as error:
        status = (404 if error.response is not None
                  and error.response.status_code == 404 else 502)
        return jsonify(error='Vocabulary data unavailable.'), status
    except (requests.RequestException, ValueError):
        return jsonify(error='Vocabulary data unavailable.'), 502


@app.route('/api/vocabulary/tree')
def vocabulary_tree() -> Response | tuple:
    """Proxy the full vocabulary tree under the global access policy."""
    return _proxy(ApiAccess.get_vocabulary_tree)


@app.route('/api/vocabulary/<int:id_>')
def vocabulary_detail(id_: int) -> Response | tuple:
    """Proxy a type detail; viewer filters are not access restrictions."""
    if id_ <= 0:
        return jsonify(error='Vocabulary type not found.'), 404
    return _proxy(lambda: ApiAccess.get_vocabulary_detail(id_))