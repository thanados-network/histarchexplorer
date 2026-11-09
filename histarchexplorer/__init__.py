import html
import os
from pathlib import Path
import secrets
import time
from typing import Any

import psycopg2.extras
from flask import Flask, g, redirect, request, session, url_for
from flask_babel import Babel
from flask_caching import Cache
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect
from psycopg2 import DatabaseError
from psycopg2.extensions import connection
from werkzeug import Response

from histarchexplorer.database.admin import (get_predefined_filters,
                                             synchronize_assets_with_db,
                                             synchronize_logos_with_db,
                                             synchronize_teams_with_db)
from histarchexplorer.models.admin import Admin
from histarchexplorer.models.config import (
    ConfigEntity, Link, Properties, get_config_classes)
from histarchexplorer.models.search import SearchService
from histarchexplorer.models.settings import Settings

_PLACEHOLDER_KEYS = {'', 'secretkey', 'CHANGE ME'}


def _load_or_generate_secret_key(flask_app: Flask) -> str:
    """Return a valid SECRET_KEY from ENV, config, or instance/.secret_key."""
    env_key = os.environ.get('SECRET_KEY', '').strip()
    if env_key and env_key not in _PLACEHOLDER_KEYS:
        return env_key

    configured = str(flask_app.config.get('SECRET_KEY') or '').strip()
    if configured and configured not in _PLACEHOLDER_KEYS:
        return configured

    instance_dir = Path(flask_app.instance_path)
    instance_dir.mkdir(parents=True, exist_ok=True)
    key_file = instance_dir / '.secret_key'

    if key_file.exists():
        stored = key_file.read_text(encoding='utf-8').strip()
        if stored and stored not in _PLACEHOLDER_KEYS:
            return stored

    new_key = secrets.token_hex(32)
    try:
        fd = os.open(
            str(key_file),
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(new_key)
        return new_key
    except FileExistsError:
        stored = key_file.read_text(encoding='utf-8').strip()
        if stored and stored not in _PLACEHOLDER_KEYS:
            return stored
        key_file.write_text(new_key, encoding='utf-8')
        os.chmod(key_file, 0o600)
        return new_key


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_object('config.admin_fields')
app.config.from_pyfile('production.py')
app.config['SECRET_KEY'] = _load_or_generate_secret_key(app)


def get_locale() -> str:
    if 'language' in session:
        return session['language']
    settings = getattr(g, 'settings', None)
    if settings:
        if settings.language_selector:
            return settings.preferred_language or 'en'
        selected = settings.selected_languages or ['en']
        return request.accept_languages.best_match(selected) or 'en'
    return request.accept_languages.best_match(app.config['LANGUAGES']) or 'en'


babel = Babel(app, locale_selector=get_locale)
cache = Cache(app)
csrf = CSRFProtect(app)
_INITIAL_SYNC_DONE = False

# pylint: disable=cyclic-import, import-outside-toplevel, wrong-import-position
from histarchexplorer.views import (
    admin, login, views, about, entity, entities, search, media, publication,
    outcome, vocabulary)
from histarchexplorer.api.api_access import ApiAccess

csrf.exempt(app.view_functions['search'])
csrf.exempt(app.view_functions['get_rastermaps'])


def connect(db_name: str) -> connection:
    try:
        connection_ = psycopg2.connect(
            database=db_name,
            user=app.config['DATABASE_USER'],
            password=app.config['DATABASE_PASS'],
            port=app.config['DATABASE_PORT'],
            host=app.config['DATABASE_HOST'])
        connection_.autocommit = True
        return connection_
    except DatabaseError as e:  # pragma: no cover
        raise DatabaseError("Database connection error.") from e




def create_icon(css_class: str) -> str:
    return f'<i class="{html.escape(css_class, quote=True)}"></i>'


def get_icon_url(filename: str) -> str:
    uploads_path = os.path.join(app.root_path, '..', 'uploads', 'icons')
    entity_icon_path = os.path.join(
        app.static_folder or '', 'images', 'entity_icons', filename)
    if os.path.exists(os.path.join(uploads_path, filename)):
        return url_for('uploaded_icon', filename=filename)
    if os.path.exists(entity_icon_path):
        return url_for('static', filename=f'images/entity_icons/{filename}')
    return url_for('static', filename=f'images/icons/{filename}')


def create_image_icon(file_name: str) -> str:
    url = get_icon_url(file_name)
    safe_alt = html.escape(file_name, quote=True)
    return f'<img src="{url}" width="16" height="16" alt="{safe_alt}"/>'


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


def get_type_divisions() -> dict[Any, dict[str, Any]]:
    out = {}
    for label, value in g.settings.type_divisions.items():
        icon = ''
        if value['icon_type'] and value['icon_value']:
            if value['icon_type'] == 'img':
                icon = create_image_icon(value['icon_value'])
            if value['icon_type'] == 'css':
                icon = create_icon(value['icon_value'])
        for id_ in value['ids']:
            out[id_] = {'label': label, 'icon': icon}
    return out


@app.before_request
def before_request() -> Response | None:
    g.db = connect(app.config['DATABASE_NAME'])
    g.cursor = g.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    g.openatlas_db = connect(app.config['OPENATLAS_DATABASE_NAME'])
    g.openatlas_cursor = g.openatlas_db.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor)

    if request.path.startswith('/reset') or request.endpoint == 'static':
        return None

    g.settings = Settings.load_from_db()
    global _INITIAL_SYNC_DONE  # pylint: disable=global-statement
    if not _INITIAL_SYNC_DONE or request.path.startswith('/admin'):
        synchronize_logos_with_db()
        synchronize_assets_with_db()
        synchronize_teams_with_db()
        _INITIAL_SYNC_DONE = True

    # Todo: move somewhere else but be aware of circular imports
    if g.settings.access_restriction:
        if not current_user.is_authenticated and request.endpoint != 'login':
            return redirect(url_for('login'))

    from flask_babel import get_locale as babel_get_locale
    g.all_languages = app.config['LANGUAGES']
    selected = g.settings.selected_languages or ['en']
    if 'en' not in selected:
        selected.append('en')
    g.available_languages = {
        k: v for k, v in g.all_languages.items() if k in selected}
    g.language = str(babel_get_locale())
    session['language'] = g.language
    if g.settings.preferred_language not in g.available_languages:
        g.settings.preferred_language = 'en'
    g.preferred_language = g.settings.preferred_language
    g.view_classes = app.config['VIEW_CLASSES']
    g.admin_fields = app.config['ADMIN_FIELDS']
    g.additional_files_for_overview = app.config['ADD_FILES_FOR_OVERVIEW']

    g.api_headers = {}
    if app.config['API_TOKEN']:
        g.api_headers["Authorization"] = f"Bearer {app.config['API_TOKEN']}"

    g.sidebar_icons = get_sidebar_icons()
    g.type_divisions = get_type_divisions()
    g.config_classes = get_config_classes()
    g.config_properties = Properties.get_all()
    g.config_links = Link.get_all()
    g.config_classes_map = {
        'projects': 1,  # option for config_class=2 project vs 1=main_project?
        'persons': 2,
        'institutions': 4,
        'attributes': 3,
        'main-project': 5}
    g.config_entities = ConfigEntity.get_all_localized()
    g.case_study_ids = [
        config.case_study for config in g.config_entities if config.case_study]
    g.search_service = SearchService(app)
    g.predefined_filters = get_predefined_filters()
    for predefined_filter in g.predefined_filters:
        for key in ('label', 'description'):
            values = predefined_filter[key]
            predefined_filter[f'{key}_values'] = values
            predefined_filter[key] = (
                values.get(g.language) or values.get(g.preferred_language)
                or values.get('en') or next(iter(values.values()), ''))

    g.pending_upgrades = []
    if current_user.is_authenticated:
        try:
            from install.upgrade import (  # type: ignore[attr-defined]
                get_pending_migrations)
            with g.db.cursor() as cur:
                g.pending_upgrades = get_pending_migrations(cur)
        except Exception:
            pass

    return None


def get_logo_url(filename: str) -> str:
    uploads_path = os.path.join(app.root_path, '..', 'uploads', 'logos')
    if os.path.exists(os.path.join(uploads_path, filename)):
        return url_for('uploaded_logo', filename=filename)
    return url_for('static', filename='images/logos/' + filename)


def get_asset_url(filename: str) -> str:
    uploads_path = os.path.join(app.root_path, '..', 'uploads', 'assets')
    if os.path.exists(os.path.join(uploads_path, filename)):
        return url_for('uploaded_asset', filename=filename)
    return url_for('static', filename='assets/' + filename)


def get_team_url(filename: str) -> str:
    uploads_path = os.path.join(app.root_path, '..', 'uploads', 'team')
    if os.path.exists(os.path.join(uploads_path, filename)):
        return url_for('uploaded_team', filename=filename)
    return url_for('static', filename='images/team/' + filename)


@app.context_processor
def inject_globals() -> dict[str, Any]:
    return {
        'settings': g.settings,
        'nav_logo': g.settings.nav_logo,
        'all_languages': g.all_languages,
        'available_languages': g.available_languages,
        'preferred_language': g.preferred_language,
        'current_language': g.language,
        'darkmode_override': g.settings.darkmode,
        'language_override': g.settings.language_selector,
        'view_classes': g.view_classes,
        'admin_fields': g.admin_fields,
        'additional_files_for_overview': g.additional_files_for_overview,
        'predefined_filters': g.predefined_filters,
        'count': 0,
        'pending_upgrades': getattr(g, 'pending_upgrades', []),
        'system_class_map': {
            "place": "places",
            "feature": "places",
            "stratigraphic_unit": "places",
            "move": "events",
            "acquisition": "events",
            "modification": "events",
            "activity": "events",
            "group": "actors",
            "person": "actors",
            "event": "events",
            "artifact": "items",
            "source": "sources",
            "file": "files",
            "type": "types"},
        'logo_id_to_filename_map': Admin.get_logo_id_to_filename_map(),
        'favicon_version': int(time.time()),
        'get_logo_url': get_logo_url,
        'get_asset_url': get_asset_url,
        'get_team_url': get_team_url,
        'get_icon_url': get_icon_url,
        'has_uploaded_favicon': os.path.exists(
            os.path.join(app.root_path, '..', 'uploads', 'favicon.ico'))}


@app.after_request
def apply_caching(response: Response) -> Response:
    response.headers['Strict-Transport-Security'] = \
        'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


@app.teardown_request
def teardown_request(exception: BaseException | None) -> None:
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

    oa_db = getattr(g, 'openatlas_db', None)
    if oa_db is not None:
        oa_db.close()
