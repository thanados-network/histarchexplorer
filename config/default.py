# Don't edit this file. To override settings please use instance/production.py
from pathlib import Path

try:
    import redis
except ImportError:
    redis = None  # type: ignore

# Application metadata
VERSION = '0.3.0'
LANGUAGES = {'de': 'Deutsch', 'en': 'English'}  # Supported languages
PREFERRED_LANGUAGE = 'en'  # Default language
DEBUG = False  # Debug mode toggle
SECRET_KEY = 'secretkey'  # Secret key for sessions and security

# Database configuration
DATABASE_NAME = 'tng'  # todo: create better name
OPENATLAS_DATABASE_NAME = 'openatlas_thanados'
DATABASE_USER = 'openatlas'
DATABASE_HOST = 'localhost'
DATABASE_PORT = 5432
DATABASE_PASS = 'CHANGE ME'  # Must be changed in production

# Security settings
SESSION_COOKIE_SECURE = False  # Use HTTPS for session cookie
REMEMBER_COOKIE_SECURE = True  # Use HTTPS for "remember me" cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection mode

ROOT_PATH = Path(__file__).parent.parent

# API configuration
API_URL = 'https://thanados.openatlas.eu/api/'
API_PROXY = ''  # Optional proxy for API requests
API_TOKEN = ''

CACHE_DEFAULT_TIMEOUT = 360000


def redis_available(url: str = "redis://127.0.0.1:6379/0") -> bool:
    if redis is None:
        return False

    try:
        r = redis.from_url(url)  # type: ignore
        r.ping()
        return True
    except Exception:
        return False


if redis_available():
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = "redis://127.0.0.1:6379/0"
else:
    CACHE_TYPE = "FileSystemCache"
    CACHE_DIR = '/tmp/flask-cache'
    CACHE_THRESHOLD = 200000
    CACHE_DEFAULT_TIMEOUT = 360000  # ensure fallback uses same TTL

# Data handling
CLASSES_TO_SKIP = {  # Entity classes excluded from processing
    'object_location', 'type', 'appellation', 'administrative_unit',
    'source_translation', 'type_tools', 'reference_system'}

# Entity groups shown in views
VIEW_CLASSES = {
    'places': ('place',),
    'features': ('feature', 'stratigraphic_unit'),
    'items': ('artifact', 'human_remains'),
    'actors': ('person', 'group'),
    'events': ('acquisition', 'event', 'activity', 'creation', 'move',
               'production', 'modification'),
    'sources': ('source', 'bibliography', 'external_reference', 'edition'),
    'files': ('file',)}

# # Commonly used standard entity types
# STANDARD_TYPES = [
#     'Source', 'Event', 'Actor function', 'Involvement', 'Bibliography',
#     'Edition', 'License', 'External reference',
#     'Source translation', 'Actor relation', 'Human remains', 'Artifact',
#     'Place', 'Feature', 'Stratigraphic unit']

ADD_FILES_FOR_OVERVIEW = 2

# Categorization of entity types with icons
TYPE_DIVISIONS = {
    'administrative unit': {
        'ids': [86],
        'icon': ('css', 'bi bi-map')},
    'dimensions': {
        'ids': [15678],
        'icon': ('css', 'bi bi-rulers')},
    'anthropology': {
        'ids': [218963, 213216, 119444, 119334],
        'icon': ('img', 'bone.svg')},
    'material': {
        'ids': [21160],
        'icon': ('img', 'material.svg')},
    'age': {
        'ids': [22277, 117198],
        'icon': ('css', 'bi bi-calendar-range')},
    'burial characteristics': {
        'ids': [213223],
        'icon': None},
    'grave characteristics': {
        'ids': [218839],
        'icon': ('img', 'grave.svg')},
    'position of find in grave': {
        'ids': [23440],
        'icon': ('css', 'bi bi-crosshair')},
    'case study': {
        'ids': [8240],
        'icon': ('css', 'bi bi-house')
        }
    }

# Icons displayed in sidebar, mapped to entity IDs
SIDEBAR_ICONS = {
    'images': {
        'grave.svg': [
            26204, 26205, 26208, 26206, 26207, 219910, 174459, 198713]},
    'css_icon_class': {
        'bi bi-geo-alt-fill': [22378, 73],
        'bi bi-house-door': [26197],
        'bi bi-geo-yelp': [13362],
        # 'bi bi-person-arms-up': [218963, 213216, 119444, 119334],
        # Anthropology
        }}

# Sidebar menu items and order
SIDEBAR_OPTIONS = [
    {'order': 1, 'route': 'overview', 'icon': 'bi bi-info-circle'},
    {'order': 2, 'route': 'map', 'icon': 'bi bi-map'},
    {'order': 3, 'route': 'media', 'icon': 'bi bi-images'},
    {'order': 4, 'route': 'catalogue', 'icon': 'bi bi-journal-text'},
    {'order': 5, 'route': 'subunits', 'icon': 'bi bi-diagram-3'},
    ]

INDIVIDUAL_PAGES = [] #if index or about should be rendered individually from index.html and about.html in the templates/individual folder
LANGUAGE_OVERRIDE = False
DARKMODE_OVERRIDE = False