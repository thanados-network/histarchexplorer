# Don't edit this file. To override settings please use instance/production.py
VERSION = '0.1.0'
LANGUAGES = {'de': 'Deutsch', 'en': 'English'}
PREFERRED_LANGUAGE = 'en'
DEBUG = True
SECRET_KEY = 'secretkey'

DATABASE_NAME = 'openatlas'
DATABASE_USER = 'openatlas'
DATABASE_HOST = 'localhost'
DATABASE_PORT = 5432
DATABASE_PASS = 'CHANGE ME'

# Security
SESSION_COOKIE_SECURE = False
REMEMBER_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Lax'

API_URL = 'https://thanados.openatlas.eu/api/'  # Todo: move to instance
API_PROXY = ''

CLASSES_TO_SKIP = ['object_location', 'type', 'appellation', 'administrative_unit', 'source_translation', 'type_tools', 'reference_system']

VIEW_CLASSES = {
    'actors': ('person','group'),
    'items': ('artifact', 'human_remains'),
    'events': ('acquisition', 'event', 'activity', 'creation', 'move',
            'production'),
    'places': ('place',),
    'sources': ('source', 'bibliography', 'external_reference', 'edition'),
    'files': ('file', 'katzen')
}