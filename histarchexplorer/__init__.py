from typing import Any

from flask import Flask, Response, session, request
from flask_babel import Babel

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_pyfile('production.py')
babel = Babel(app)

# pylint: disable=cyclic-import, import-outside-toplevel, wrong-import-position
from histarchexplorer import util, views


@babel.localeselector
def get_locale() -> str:
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(app.config['LANGUAGES']) or 'en'


@app.context_processor
def inject_conf_var() -> dict[str, Any]:
    return {
        'AVAILABLE_LANGUAGES': app.config['LANGUAGES'],
        'CURRENT_LANGUAGE': session.get(
            'language',
            request.accept_languages.best_match(
                app.config['LANGUAGES'].keys()))}


@app.after_request
def apply_caching(response: Response) -> Response:
    response.headers['Strict-Transport-Security'] = \
        'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
