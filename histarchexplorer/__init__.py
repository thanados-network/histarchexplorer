from typing import Any

import psycopg2.extras
from flask import Flask, Response, g, request, session, url_for
from flask_babel import Babel
from psycopg2 import DatabaseError
from psycopg2.extensions import connection

from histarchexplorer.database.settings import get_main_image_table
from histarchexplorer.services.config import get_config_types
from histarchexplorer.services.config_entities import ConfigEntity, \
    RelationshipLabel
from histarchexplorer.services.search import SearchService
from histarchexplorer.services.settings import Settings

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_pyfile('production.py')
babel = Babel(app)

# pylint: disable=cyclic-import, import-outside-toplevel, wrong-import-position
from histarchexplorer.views import (
    admin, login, views, about, entity, landing, search)
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
    except DatabaseError as e:  # pragma: no cover
        raise DatabaseError("Database connection error.") from e


@babel.localeselector
def get_locale() -> str:
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(app.config['LANGUAGES']) or 'en'


def create_icon(css_class: str) -> str:
    return f'<i class="{css_class}"></i>'


def create_image_icon(file_name: str) -> str:
    filepath = url_for("static", filename="images/entity_icons/")
    return (f'<img src="{filepath + file_name}" '
            f'width="16" height="16" alt="{file_name}"/>')


def get_sidebar_icons() -> dict[int, str]:
    type_icons = app.config['SIDEBAR_ICONS']
    icons = {}
    for image, ids in type_icons['images'].items():
        image_tag = create_image_icon(image)
        for id_ in ids:
            icons[id_] = image_tag
    for icon, ids in type_icons['css_icon_class'].items():
        icon_tag = create_icon(icon)
        for id_ in ids:
            icons[id_] = icon_tag
    icons['other'] = '<i class="bi bi-box-arrow-left"></i>'
    return icons


def get_type_divisions():
    out = {}
    for label, value in app.config['TYPE_DIVISIONS'].items():
        icon = ''
        if value['icon']:
            if value['icon'][0] == 'img':
                icon = create_image_icon(value['icon'][1])
            if value['icon'][0] == 'css':
                icon = create_icon(value['icon'][1])
        for id_ in value['ids']:
            out[id_] = {'label': label, 'icon': icon}
    return out


@app.before_request
def before_request() -> None:
    g.db = connect()
    g.cursor = g.db.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    if request.path.startswith('/reset'):
        return None
    session['language'] = get_locale()
    g.language = session.get(
        'language',
        request.accept_languages.best_match(app.config['LANGUAGES'].keys()))
    g.preferred_langauge = app.config['PREFERRED_LANGUAGE']
    g.main_images = get_main_image_table()
    g.sidebar_icons = get_sidebar_icons()
    g.type_divisions = get_type_divisions()
    g.config_types = get_config_types()
    g.config_relationship_labels = RelationshipLabel.get_all()
    g.settings = Settings.initialize_settings()
    # Todo: this is basically the same as
    #   config_classes but with 's' and attributes instead of attribute
    g.config_types_map = {
        'projects': 1,  # option for config_class=2 project vs 1=main_project?
        'persons': 2,
        'institutions': 4,
        'attributes': 3,
        'main-project': 5}
    g.config_entities = ConfigEntity.get_all_localized()
    g.search_service = SearchService(app)
    return None


@app.context_processor
def inject_conf_var() -> dict[str, Any]:
    return {
        'AVAILABLE_LANGUAGES': app.config['LANGUAGES'],
        'PREFERRED_LANGUAGE': app.config['PREFERRED_LANGUAGE'],
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
