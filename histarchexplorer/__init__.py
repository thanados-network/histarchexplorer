from typing import Any

import psycopg2.extras

from flask import Flask, g, Response, session, request
from flask_babel import Babel

from psycopg2.extensions import connection

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_pyfile('production.py')
babel = Babel(app)

# pylint: disable=cyclic-import, import-outside-toplevel, wrong-import-position
from histarchexplorer.views import admin, login, test_entity, views, about
from histarchexplorer.utils import view_util

def connect() -> connection:
    try:
        connection_ = psycopg2.connect(
            database=app.config['DATABASE_NAME'],
            user=app.config['DATABASE_USER'],
            password=app.config['DATABASE_PASS'],
            port=app.config['DATABASE_PORT'],
            host=app.config['DATABASE_HOST'])
        connection_.autocommit = True
        return connection_
    except Exception as e:  # pragma: no cover
        print("Database connection error.")
        raise Exception(e)


@babel.localeselector
def get_locale() -> str:
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(app.config['LANGUAGES']) or 'en'


@app.before_request
def before_request() -> None:
    g.db = connect()
    g.cursor = g.db.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    session['language'] = get_locale()


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
