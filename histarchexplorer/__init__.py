from typing import Any

from flask import Flask, Response, session, request, redirect
from flask_babel import Babel
from flask_babel import lazy_gettext as _

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_pyfile('production.py')
babel = Babel(app)

# pylint: disable=cyclic-import, import-outside-toplevel, wrong-import-position
from histarchexplorer import views

@babel.localeselector
def get_locale() -> str:
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(app.config['LANGUAGES']) or 'en'

@app.route('/language/<language>')
def set_language(language: str) -> Response:
    if language in app.config['LANGUAGES']:
        session['language'] = language
    if request.referrer is not None:
        return redirect(request.referrer)
    else:
        # If referrer is None, redirect to some default page
        return redirect('/')

@app.context_processor
def inject_conf_var() -> dict[str, Any]:
    return {
        'AVAILABLE_LANGUAGES': app.config['LANGUAGES'],
        'CURRENT_LANGUAGE': session.get(
            'language',
            request.accept_languages.best_match(
                app.config['LANGUAGES'].keys())),
        'NAVBAR_ELEMENTS': [
            {'original': 'entities', session['language']: _('entities'), 'title': _('browse/select/find all entities')},
            {'original': 'search', session['language']: _('search'), 'title': _('detailed search')},
            {'original': 'about', session['language']: _('about'), 'title': _('about the project')}],
    }

@app.before_request
def before_request() -> None:
    session['language'] = get_locale()

@app.after_request
def apply_caching(response: Response) -> Response:
    response.headers['Strict-Transport-Security'] = \
        'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
