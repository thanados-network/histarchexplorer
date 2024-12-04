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

API_URL = 'https://thanados.openatlas.eu/api/'
API_PROXY = ''
OPENATLAS_CASE_STUDY_IDS: list[int] = []

CLASSES_TO_SKIP = [
    'object_location', 'type', 'appellation', 'administrative_unit',
    'source_translation', 'type_tools', 'reference_system']

VIEW_CLASSES = {
    'actors': ('person', 'group'),
    'items': ('artifact', 'human_remains'),
    'events': ('acquisition', 'event', 'activity', 'creation', 'move',
               'production', 'modification'),
    'places': ('place', 'stratigraphic_unit', 'feature'),
    'sources': ('source', 'bibliography', 'external_reference', 'edition'),
    'files': ('file',)
}

STANDARD_TYPES = [
    'Source', 'Event', 'Actor function', 'Involvement', 'Bibliography',
    'Edition', 'License', 'External reference',
    'Source translation', 'Actor relation', 'Human remains', 'Artifact',
    'Place', 'Feature', 'Stratigraphic unit']

TYPE_DIVISIONS = {
    'dimensions': [15678],
    'anthropology': [218963, 213216, 119444, 119334],
    'material': [21160],
    'age': [22277, 117198],
    'burial characteristics': [213223],
    'grave characteristics': [218839]
}

TYPE_ICONS = {
    'images': {
        'grave.svg': [26204, 26205, 26208, 26206, 26207, 219910, 174459, 198713 ],
        'bone.svg': [218963, 213216, 119444, 119334], # Anthroplogy
    },
    'css_icon_class': {
        'bi bi-geo-alt-fill': [22378, 73],
        'bi bi-house-door': [26197],
        'bi bi-geo-yelp': [13362],
        'bi bi-rulers': [15678],  # Dimensions
        'bi bi-calendar-range': [22277, 117198],  # Age
        #'bi bi-person-arms-up': [218963, 213216, 119444, 119334], # Anthroplogy
    }}
