"""
Settings para tests — Usa SQLite en memoria para evitar problemas con MySQL
"""
from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Desactivar logging durante tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}
