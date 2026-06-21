"""
Settings para previsualización en v0 — usa SQLite en archivo para persistir datos.
NO usar en producción (producción usa MySQL en settings.py).
"""
from .settings import *  # noqa
import os

DEBUG = True
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.run', 'https://*.v0.dev', 'http://localhost', 'http://127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db_dev.sqlite3'),
    }
}
