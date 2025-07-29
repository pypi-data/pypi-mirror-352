"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import os
import pathlib
from aixblock_core.core.settings.base import *
from aixblock_core.core.settings.jobs import *

DJANGO_DB = get_env('DJANGO_DB', DJANGO_DB_SQLITE)
DATABASES = {'default': DATABASES_ALL[DJANGO_DB]}

MIDDLEWARE.append('organizations.middleware.DummyGetSessionMiddleware')
MIDDLEWARE.append('core.middleware.UpdateLastActivityMiddleware')

ADD_DEFAULT_ML_BACKENDS = False

LOGGING['root']['level'] = get_env('LOG_LEVEL', 'WARNING')

DEBUG = get_bool_env('DEBUG', False)

DEBUG_PROPAGATE_EXCEPTIONS = get_bool_env('DEBUG_PROPAGATE_EXCEPTIONS', False)

SESSION_COOKIE_SECURE = False

# SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
# SESSION_ENGINE = "django.contrib.sessions.backends.db"

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
# SESSION_ENGINE = 'django_redis_session_store.session_store'
SESSION_REDIS_HOST = get_env('SESSION_REDIS_HOST', 'localhost')
SESSION_REDIS_PORT = int(get_env('SESSION_REDIS_PORT', 6379))
SESSION_REDIS_DB = get_env('SESSION_REDIS_DB', 0)
SESSION_REDIS_PASSWORD = get_env('SESSION_REDIS_PASSWORD', '')
SESSION_REDIS_USER =get_env('SESSION_REDIS_USER', '')
SESSION_REDIS_PREFIX = get_env('SESSION_REDIS_PREFIX', 'session')
SESSION_REDIS_SOCKET_TIMEOUT = get_env('SESSION_REDIS_SOCKET_TIMEOUT', 1800)
SESSION_REDIS_TLS = get_bool_env('SESSION_REDIS_TLS', False)
SHARED_SECRET_KEY = get_env('SHARED_SECRET_KEY', '42d8236921664c1fb7097455e9e9c6ea')
MINIO_SECRET_KEY = get_env(
    "MINIO_SECRET_KEY",
    "gLrD5R4bkK1sS3Cci4pH9qWp9jHg6QrMlvBt7XUyK5fO2PbPiZjT2KD0O8TR3k1UYPB6",
)

# SENTRY_DSN = get_env(
#     'SENTRY_DSN',
#     'https://42d8236921664c1fb7097455e9e9c6ea@o391799.ingest.sentry.io/4504393308176384'
# )
# SENTRY_ENVIRONMENT = get_env('SENTRY_ENVIRONMENT', 'opensource')
#
# FRONTEND_SENTRY_DSN = get_env(
#     'FRONTEND_SENTRY_DSN',
#     'https://7a6c6539e2064131901a7816c1dac64e@o391799.ingest.sentry.io/4504393305161728')
# FRONTEND_SENTRY_ENVIRONMENT = get_env('FRONTEND_SENTRY_ENVIRONMENT', 'opensource')

EDITOR_KEYMAP = json.dumps(get_env("EDITOR_KEYMAP"))
# from aixblock_core.core.version import info
# from ..utils import sentry
# sentry.init_sentry(release_name='aixblock', release_version="2.1.2")

# we should do it after sentry init
# from ..utils.common import collect_versions
# versions = collect_versions()

# in AiXBlock Community version, feature flags are always ON
FEATURE_FLAGS_DEFAULT_VALUE = True
# or if file is not set, default is using offline mode
FEATURE_FLAGS_OFFLINE = get_bool_env('FEATURE_FLAGS_OFFLINE', True)

from aixblock_core.core.utils.io import find_file
FEATURE_FLAGS_FILE = get_env('FEATURE_FLAGS_FILE', 'feature_flags.json')
FEATURE_FLAGS_FROM_FILE = True
# try:
#     from ..utils.io import find_node
#     find_node('aixblock_core', FEATURE_FLAGS_FILE, 'file')
# except IOError:
#     FEATURE_FLAGS_FROM_FILE = False

STORAGE_PERSISTENCE = get_bool_env('STORAGE_PERSISTENCE', True)
