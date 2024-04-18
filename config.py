# Don't edit this file. To override settings please use instance/production.py
from pathlib import Path

VERSION = '0.1.0'
LANGUAGES = {'de': 'Deutsch', 'en': 'English'}
DEBUG = False
SECRET_KEY = '1E600383250F0F63E9627E650B683DCE'

# Security
SESSION_COOKIE_SECURE = False
REMEMBER_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Lax'

ROOT_PATH = Path(__file__)

STATIC_PATH = ROOT_PATH / 'static'
IMAGE_PATH = STATIC_PATH / 'images'
THUMBNAIL_PATH = STATIC_PATH / 'thumbnails'

