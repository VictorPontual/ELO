# Test-only settings: local SQLite DB so we never touch production Supabase.
# Not for deploy. Safe to delete.
import os
os.environ.setdefault('DJANGO_SECRET_KEY', 'localtest-secret-key')
os.environ['DJANGO_DEBUG'] = 'True'
os.environ.pop('DATABASE_URL', None)

from .settings import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_local_test.sqlite3',
    }
}
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Dev local por HTTP: desliga tudo que exige HTTPS, independente do que o .env
# tiver (o .env pode estar com DJANGO_SECURE_SSL=True por causa do deploy).
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
