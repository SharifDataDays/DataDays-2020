import os

from .development import *


SECRET_KEY = 'oaeu#@$puoeuj,#$>Ueok,4IY@#$"PU.ohukAEOUO>AYU34$IPK'

DEBUG = True

ALLOWED_HOSTS = ['*']

WSGI_APPLICATION = 'thebackend.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "datadays",
        "USER": "datadaysuser",
        "PASSWORD": "datadayspassword",
        "HOST": "postgres",
        "PORT": "5432",
    }
}

LOG_ROOT = "/log/datadays"

TIME_ZONE = 'Iran'

STATIC_URL = '/static/'
STATIC_ROOT = '/files/datadays/static'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/files/datadays/media'

CSRF_COOKIE_HTTPONLY = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "sharif.datadays.3@gmail.com"
EMAIL_HOST_PASSWORD = "datadays_branding"
EMAIL_PORT = "587"

import datetime
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=5),
}


CELERY_BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = 'amqp'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

