import os

from .base import *

# Parse database configuration from $DATABASE_URL
import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

ALLOWED_HOSTS = ['morning-eyrie-79104.herokuapp.com']

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

DEBUG = False

SENDGRID_USERNAME = os.environ.get('SENDGRID_USERNAME', None)
SENDGRID_PASSWORD = os.environ.get('SENDGRID_PASSWORD', None)
