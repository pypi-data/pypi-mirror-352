"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
Django Base settings for AIxBlock Tool.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import binascii
import json
import logging
import os
import re
import stripe
from aixblock_core.core.utils.params import get_bool_env

formatter = 'standard'
JSON_LOG = get_bool_env('JSON_LOG', False)
if JSON_LOG:
    formatter = 'json'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'aixblock_core.core.utils.formatter.CustomJsonFormatter',
            'format': '[%(asctime)s] [%(name)s::%(funcName)s::%(lineno)d] [%(levelname)s] [%(user_id)s] %(message)s',
            'datefmt': '%d/%b/%Y:%H:%M:%S %z',
        },
        'standard': {
            'format': '[%(asctime)s] [%(name)s::%(funcName)s::%(lineno)d] [%(levelname)s] %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': formatter,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'DEBUG'),
    },
    'loggers': {
        'pykwalify': {'level': 'ERROR', 'propagate': False},
        'tavern': {'level': 'ERROR', 'propagate': False},
        'asyncio': {'level': 'WARNING'},
        'rules': {'level': 'WARNING'},
        'django': {
            'handlers': ['console'],
            # 'propagate': True,
        },
        'django_auth_ldap': {'level': os.environ.get('LOG_LEVEL', 'DEBUG')},
        "rq.worker": {
            "handlers": ["console"],
            "level": os.environ.get('LOG_LEVEL', 'INFO'),
        },
        'ddtrace': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}


# for printing messages before main logging config applied
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

from aixblock_core.core.utils.io import get_data_dir
from aixblock_core.core.utils.params import (get_bool_env, get_env)

logger = logging.getLogger(__name__)
SILENCED_SYSTEM_CHECKS = []

# Hostname is used for proper path generation to the resources, pages, etc
HOSTNAME = get_env('HOST', '')
if HOSTNAME:
    if not HOSTNAME.startswith('http://') and not HOSTNAME.startswith('https://'):
        logger.info(
            "! HOST variable found in environment, but it must start with http:// or https://, ignore it: %s", HOSTNAME
        )
        HOSTNAME = ''
    else:
        logger.info("=> Hostname correctly is set to: %s", HOSTNAME)
        if HOSTNAME.endswith('/'):
            HOSTNAME = HOSTNAME[0:-1]

        # for django url resolver
        if HOSTNAME:
            # http[s]://domain.com/script_name => /script_name
            pattern = re.compile(r'^http[s]?:\/\/([^:\/\s]+(:\d*)?)(.*)?')
            match = pattern.match(HOSTNAME)
            FORCE_SCRIPT_NAME = match.group(3)
            if FORCE_SCRIPT_NAME:
                logger.info("=> Django URL prefix is set to: %s", FORCE_SCRIPT_NAME)

# if not HOSTNAME.endswith("/"):
#     HOSTNAME += "/"

INTERNAL_PORT = get_env('AXB_PUBLIC_PORT', 8080) 

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool_env('DEBUG', False)
DEBUG_MODAL_EXCEPTIONS = get_bool_env('DEBUG_MODAL_EXCEPTIONS', True)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = get_env('BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  #os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Base path for media root and other uploaded files
BASE_DATA_DIR = get_env('BASE_DATA_DIR', get_data_dir())
os.makedirs(BASE_DATA_DIR, exist_ok=True)
logger.info('=> Database and media directory: %s', BASE_DATA_DIR)

# Databases
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DJANGO_DB_MYSQL = 'mysql'
DJANGO_DB_SQLITE = 'sqlite'
DJANGO_DB_POSTGRESQL = 'postgresql'
DJANGO_DB = 'default'
DATABASE_NAME_DEFAULT = os.path.join(BASE_DATA_DIR, 'aixblock_core.sqlite3')
DATABASE_NAME = get_env('DATABASE_NAME', DATABASE_NAME_DEFAULT)
DATABASES_ALL = {
    # DJANGO_DB_POSTGRESQL: {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'USER': get_env('POSTGRES_USER', 'postgres'),
    #     'PASSWORD': get_env('POSTGRES_PASSWORD', '@9^xwWA'),
    #     'NAME': get_env('POSTGRES_NAME', 'tool_datasets_live'),
    #     'HOST': get_env('POSTGRES_HOST', '108.181.196.144'),
    #     'PORT': int(get_env('POSTGRES_PORT', '5432')),
    # },
    DJANGO_DB_POSTGRESQL: {
        "ENGINE": "django.db.backends.postgresql",
        "USER": get_env("POSTGRES_USER", "postgres"),
        "PASSWORD": get_env("POSTGRES_PASSWORD", "@9^xwWA"),
        "NAME": get_env("POSTGRES_NAME", "platform_v2"),
        "HOST": get_env("POSTGRES_HOST", "localhost"),
        "PORT": int(get_env("POSTGRES_PORT", "5432")),
    },
    # DJANGO_DB_MYSQL: {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'USER': get_env('MYSQL_USER', 'root'),
    #     'PASSWORD': get_env('MYSQL_PASSWORD', '@9^xwWA'),
    #     'NAME': get_env('MYSQL_NAME', 'tool_datasets_live'),
    #     'HOST': get_env('MYSQL_HOST', '172.17.0.1'),
    #     'PORT': int(get_env('MYSQL_PORT', '3306')),
    # },
    DJANGO_DB_SQLITE: {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATABASE_NAME,
        "OPTIONS": {
            # 'timeout': 20,
        },
    },
}
DATABASES_ALL['default'] = DATABASES_ALL[DJANGO_DB_POSTGRESQL]
DATABASES = {'default': DATABASES_ALL.get(get_env('DJANGO_DB', DJANGO_DB_POSTGRESQL))}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


if get_bool_env('GOOGLE_LOGGING_ENABLED', False):
    logging.info('Google Cloud Logging handler is enabled.')
    try:
        import google.cloud.logging
        from google.auth.exceptions import GoogleAuthError

        client = google.cloud.logging.Client()
        client.setup_logging()

        LOGGING['handlers']['google_cloud_logging'] = {
            'level': get_env('LOG_LEVEL', 'WARNING'),
            'class': 'google.cloud.logging.handlers.CloudLoggingHandler',
            'client': client,
        }
        LOGGING['root']['handlers'].append('google_cloud_logging')
    except GoogleAuthError as e:
        logger.exception('Google Cloud Logging handler could not be setup.')

INSTALLED_APPS = [
    'model_prefix',
    # 'admin_volt.apps.AdminVoltConfig',
    "sslserver",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'drf_yasg',
    'corsheaders',
    'django_extensions',
    'django_rq',
    'django_filters',
    'rules',
    'annoying',
    'rest_framework',
    'rest_framework_swagger',
    'rest_framework.authtoken',
    'drf_generators',
    'core',
    'users',
    'organizations',
    'data_import',
    'data_export',
    'projects',
    'tasks',
    'data_manager',
    'io_storages',
    'ml',
    'webhooks',
    'labels_manager',
    'oauth2_provider',
    'comments',
    'model_marketplace',
    'annotation_template',
    'compute_marketplace',
    'tutorials',
    'orders',
    'reward_point',
    'paypal',
    'configs',
    'stripe_payment',
    'django_dbq',
    'workflows',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'core.middleware.DisableCSRF',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.CommonMiddlewareAppendSlashWithoutRedirect',  # instead of 'CommonMiddleware'
    'core.middleware.CommonMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'core.middleware.SetSessionUIDMiddleware',
    'core.middleware.ContextLogMiddleware',
    'core.middleware.DatabaseIsLockedRetryMiddleware',
    'core.current_request.ThreadLocalMiddleware',
    #oauth call ai hackathon
    'core.middleware.OAuthMiddleware',
    'core.middleware.StaticCacheHeader',
    'oauth2_provider.middleware.OAuth2TokenMiddleware'
]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'core.api_permissions.HasObjectPermission',
        'rest_framework.permissions.IsAuthenticated',
    ],
    'EXCEPTION_HANDLER': 'core.utils.common.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'PAGE_SIZE': 100,
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination'
}
SILENCED_SYSTEM_CHECKS += ["rest_framework.W001"]

# CORS & Host settings
INTERNAL_IPS = [  # django debug toolbar for django==2.2 requirement
 
    '127.0.0.1',
    'localhost',
]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
         #live server
        # 'https://app.aixblock.io:5000',
        # 'https://app.aixblock.io:9091',
        # 'https://app.aixblock.io:9090',
    ]

BASE_BACKEND_URL = get_env("BASE_BACKEND_URL", "https://app.aixblock.io")
REVERSE_IP = get_env("REVERSE_IP", "reverse.aixblock.io")
REVERSE_ADDRESS = get_env("REVERSE_ADDRESS", "tcp://207.246.109.178:4243")
URL_CONVERT = get_env("URL_CONVERT", "http://207.246.109.178:1290/api/serve")
TOKEN_URL_CONVERT = get_env("TOKEN_URL_CONVERT", "")
DASHBOARD_URL = get_env("DASHBOARD_URL", "http://207.246.109.178:3000/d/edofrn4oh4wsga/docker-host?orgId=1&refresh=10s&from=1718346892406&to=1718347792406")
DASHBOARD_IP = get_env("DASHBOARD_IP", "http://207.246.109.178:3000")
INSTALL_TYPE = get_env("HOST_IP", "PLATFORM")

# Auth modules
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = ['rules.permissions.ObjectPermissionBackend', 'django.contrib.auth.backends.ModelBackend',]
USE_USERNAME_FOR_LOGIN = False

DISABLE_SIGNUP_WITHOUT_LINK = get_bool_env('DISABLE_SIGNUP_WITHOUT_LINK', False)

SESSION_REDIS_HOST = os.environ.get("SESSION_REDIS_HOST", "localhost")

# Password validation:
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Django templates
TEMPLATES_DIR = os.path.join(os.path.dirname(BASE_DIR), 'templates')  # ../../from_this = 'web' dir
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.settings',
            ],
            'builtins': ['django.templatetags.i18n'],
        },
    }
]
# RQ
RQ_REDIS_HOST = os.environ.get("RQ_REDIS_HOST", None)
RQ_REDIS_PORT = int(os.environ.get("RQ_REDIS_PORT", 0))
RQ_REDIS_DB = int(os.environ.get("RQ_REDIS_DB", 0))
RQ_QUEUES = {
    'custom': {
        'HOST': RQ_REDIS_HOST,
        'PORT': RQ_REDIS_PORT,
        'DB': RQ_REDIS_DB,
        'DEFAULT_TIMEOUT': 180,
        'ASYNC': RQ_REDIS_HOST is not None,
    },
    'critical': {
        'HOST': RQ_REDIS_HOST,
        'PORT': RQ_REDIS_PORT,
        'DB': RQ_REDIS_DB,
        'DEFAULT_TIMEOUT': 180,
        'ASYNC': RQ_REDIS_HOST is not None,
    },
    'high': {
        'HOST': RQ_REDIS_HOST,
        'PORT': RQ_REDIS_PORT,
        'DB': RQ_REDIS_DB,
        'DEFAULT_TIMEOUT': 180,
        'ASYNC': RQ_REDIS_HOST is not None,
    },
    'default': {
        'HOST': RQ_REDIS_HOST,
        'PORT': RQ_REDIS_PORT,
        'DB': RQ_REDIS_DB,
        'DEFAULT_TIMEOUT': 180,
        'ASYNC': RQ_REDIS_HOST is not None,
    },
    'low': {
        'HOST': RQ_REDIS_HOST,
        'PORT': RQ_REDIS_PORT,
        'DB': RQ_REDIS_DB,
        'DEFAULT_TIMEOUT': 180,
        'ASYNC': RQ_REDIS_HOST is not None,
    },
}

# Swagger: automatic API documentation
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description':
                'The token (or API key) must be passed as a request header. '
                'You can find your user token on the User Account page in AIxBlock Tool. Example: '
                '<br><pre><code class="language-bash">'
                'curl https://app.aixblock.io/api/projects -H "Authorization: Token [your-token]"'
                '</code></pre>'
        }
    },
    'APIS_SORTER': 'alpha',
    'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'put', 'delete', 'patch'],
    'OPERATIONS_SORTER': 'alpha',
    'DEEP_LINKING': True
}

SENTRY_DSN = get_env('SENTRY_DSN', None)
SENTRY_RATE = float(get_env('SENTRY_RATE', 0.25))
SENTRY_ENVIRONMENT = get_env('SENTRY_ENVIRONMENT', 'stage.opensource')
SENTRY_REDIS_ENABLED = False
FRONTEND_SENTRY_DSN = get_env('FRONTEND_SENTRY_DSN', None)
FRONTEND_SENTRY_RATE = get_env('FRONTEND_SENTRY_RATE', 0.1)
FRONTEND_SENTRY_ENVIRONMENT = get_env('FRONTEND_SENTRY_ENVIRONMENT', 'stage.opensource')

ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'
GRAPHIQL = True

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'
# if FORCE_SCRIPT_NAME:
#    STATIC_URL = FORCE_SCRIPT_NAME + STATIC_URL
logger.info(f'=> Static URL is set to: {STATIC_URL}')

STATIC_ROOT = os.path.join(BASE_DIR, 'static_build')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATICFILES_STORAGE = 'core.storage.SkipMissedManifestStaticFilesStorage'

# Sessions and CSRF
SESSION_COOKIE_SECURE = bool(int(get_env('SESSION_COOKIE_SECURE', False)))
CSRF_COOKIE_SECURE = bool(int(get_env('CSRF_COOKIE_SECURE', SESSION_COOKIE_SECURE)))
CSRF_COOKIE_HTTPONLY = bool(int(get_env('CSRF_COOKIE_HTTPONLY', SESSION_COOKIE_SECURE)))

SSRF_PROTECTION_ENABLED = get_bool_env('SSRF_PROTECTION_ENABLED', False)

# user media files
MEDIA_ROOT = os.path.join(BASE_DATA_DIR, 'media')
os.makedirs(MEDIA_ROOT, exist_ok=True)
MEDIA_URL = '/data/'
UPLOAD_DIR = 'upload'
AVATAR_PATH = 'avatars'

# project exports
EXPORT_DIR = os.path.join(BASE_DATA_DIR, 'export')
EXPORT_URL_ROOT = '/export/'
EXPORT_MIXIN = 'data_export.mixins.ExportMixin'
# old export dir
os.makedirs(EXPORT_DIR, exist_ok=True)
# dir for delayed export
DELAYED_EXPORT_DIR = 'export'
os.makedirs(os.path.join(BASE_DATA_DIR, MEDIA_ROOT, DELAYED_EXPORT_DIR), exist_ok=True)

# file / task size limits
DATA_UPLOAD_MAX_MEMORY_SIZE = int(get_env('DATA_UPLOAD_MAX_MEMORY_SIZE', 250 * 1024 * 1024))
TASKS_MAX_NUMBER = 1000000
TASKS_MAX_FILE_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE

TASK_LOCK_TTL = int(get_env('TASK_LOCK_TTL')) if get_env('TASK_LOCK_TTL') else None
TASK_LOCK_DEFAULT_TTL = int(get_env('TASK_LOCK_DEFAULT_TTL', 3600))
TASK_LOCK_MIN_TTL = int(get_env('TASK_LOCK_MIN_TTL', 120))

RANDOM_NEXT_TASK_SAMPLE_SIZE = int(get_env('RANDOM_NEXT_TASK_SAMPLE_SIZE', 50))

TASK_API_PAGE_SIZE_MAX = int(get_env('TASK_API_PAGE_SIZE_MAX', 0)) or None

# Email backend
FROM_EMAIL = get_env('FROM_EMAIL', 'AIxBlock Tool <contact@wow-ai.com>')
EMAIL_BACKEND = get_env('EMAIL_BACKEND', 'django.core.mail.backends.dummy.EmailBackend')

ENABLE_LOCAL_FILES_STORAGE = get_bool_env('ENABLE_LOCAL_FILES_STORAGE', default=True)
LOCAL_FILES_SERVING_ENABLED = get_bool_env('LOCAL_FILES_SERVING_ENABLED', default=False)
LOCAL_FILES_DOCUMENT_ROOT = get_env('LOCAL_FILES_DOCUMENT_ROOT', default=os.path.abspath(os.sep))

SYNC_ON_TARGET_STORAGE_CREATION = get_bool_env('SYNC_ON_TARGET_STORAGE_CREATION', default=True)

""" React Libraries: do not forget to change this dir in /etc/nginx/nginx.conf """
# EDITOR = aixblock-frontend repository
UI_DIR = get_env('UI_DIR', BASE_DIR)
EDITOR_ROOT = os.path.join(UI_DIR, 'general-editor/build/static')
# DM = data manager (included into FRONTEND due npm building, we need only version.json file from there)
# DM_ROOT = os.path.join(UI_DIR, '../frontend/dist/dm')
# FRONTEND = GUI for django backend
REACT_APP_ROOT = os.path.join(UI_DIR, 'frontend/dist/react-app')
# New UI root

UI_ROOT = os.path.join(UI_DIR, 'frontend/build')
RIA_ROOT = os.path.join(UI_DIR, 'react-image-annotate/build')
TDE_ROOT = os.path.join(UI_DIR, 'three-dimensional-editor/build')
LLM_ROOT = os.path.join(UI_DIR, 'tool-llm-editor/build')

# per project settings
BATCH_SIZE = 1000
PROJECT_TITLE_MIN_LEN = 3
PROJECT_TITLE_MAX_LEN = 50
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/'
MIN_GROUND_TRUTH = 10
DATA_UNDEFINED_NAME = '$undefined$'
LICENSE = {}
VERSIONS = {}
VERSION_EDITION = 'Community'
LATEST_VERSION_CHECK = True
VERSIONS_CHECK_TIME = 0
ALLOW_ORGANIZATION_WEBHOOKS = get_bool_env('ALLOW_ORGANIZATION_WEBHOOKS', False)
CONVERTER_DOWNLOAD_RESOURCES = get_bool_env('CONVERTER_DOWNLOAD_RESOURCES', True)
EXPERIMENTAL_FEATURES = get_bool_env('EXPERIMENTAL_FEATURES', False)
USE_ENFORCE_CSRF_CHECKS = get_bool_env('USE_ENFORCE_CSRF_CHECKS', True)  # False is for tests
CLOUD_FILE_STORAGE_ENABLED = False

IO_STORAGES_IMPORT_LINK_NAMES = [
    'io_storages_s3importstoragelink',
    'io_storages_gcsimportstoragelink',
    'io_storages_azureblobimportstoragelink',
    'io_storages_localfilesimportstoragelink',
    'io_storages_redisimportstoragelink',
    'io_storages_gdriverimportstoragelink',
]

CREATE_ORGANIZATION = 'organizations.functions.create_organization'
GET_OBJECT_WITH_CHECK_AND_LOG = 'core.utils.get_object.get_object_with_check_and_log'
SAVE_USER = 'users.functions.save_user'
USER_SERIALIZER = 'users.serializers.BaseUserSerializer'
TASK_SERIALIZER = 'tasks.serializers.BaseTaskSerializer'
EXPORT_DATA_SERIALIZER = 'data_export.serializers.BaseExportDataSerializer'
DATA_MANAGER_GET_ALL_COLUMNS = 'data_manager.functions.get_all_columns'
DATA_MANAGER_ANNOTATIONS_MAP = {}
DATA_MANAGER_ACTIONS = {}
DATA_MANAGER_CUSTOM_FILTER_EXPRESSIONS = 'data_manager.functions.custom_filter_expressions'
DATA_MANAGER_PREPROCESS_FILTER = 'data_manager.functions.preprocess_filter'
USER_LOGIN_FORM = 'users.forms.LoginForm'
PROJECT_MIXIN = 'core.mixins.DummyModelMixin'
TASK_MIXIN = 'tasks.mixins.TaskMixin'
ANNOTATION_MIXIN = 'tasks.mixins.AnnotationMixin'
ORGANIZATION_MIXIN = 'organizations.mixins.OrganizationMixin'
USER_MIXIN = 'users.mixins.UserMixin'
GET_STORAGE_LIST = 'io_storages.functions.get_storage_list'
STORAGE_ANNOTATION_SERIALIZER = 'io_storages.serializers.StorageAnnotationSerializer'
TASK_SERIALIZER_BULK = 'tasks.serializers.BaseTaskSerializerBulk'
PREPROCESS_FIELD_NAME = 'data_manager.functions.preprocess_field_name'
INTERACTIVE_DATA_SERIALIZER = 'data_export.serializers.BaseExportDataSerializerForInteractive'
DELETE_TASKS_ANNOTATIONS_POSTPROCESS = None


def project_delete(project):
    project.delete()


def user_auth(user_model, email, password):
    return None


def collect_versions_dummy(**kwargs):
    return {}


PROJECT_DELETE = project_delete
USER_AUTH = user_auth
COLLECT_VERSIONS = collect_versions_dummy

WEBHOOK_TIMEOUT = float(get_env('WEBHOOK_TIMEOUT', 1.0))
WEBHOOK_SERIALIZERS = {
    'project': 'webhooks.serializers_for_hooks.ProjectWebhookSerializer',
    'task': 'webhooks.serializers_for_hooks.TaskWebhookSerializer',
    'annotation': 'webhooks.serializers_for_hooks.AnnotationWebhookSerializer',
    'label': 'labels_manager.serializers.LabelSerializer',
    'label_link': 'labels_manager.serializers.LabelLinkSerializer',
}

EDITOR_KEYMAP = json.dumps(get_env("EDITOR_KEYMAP"))

# fix a problem with Windows mimetypes for JS and PNG
import mimetypes

mimetypes.add_type("application/javascript", ".js", True)
mimetypes.add_type("image/png", ".png", True)

# fields name was used in DM api before
REST_FLEX_FIELDS = {"FIELDS_PARAM": "include"}

INTERPOLATE_KEY_FRAMES = get_env('INTERPOLATE_KEY_FRAMES', False)

# Feature Flags
FEATURE_FLAGS_API_KEY = get_env('FEATURE_FLAGS_API_KEY', default='any key')

# we may set feature flags from file
FEATURE_FLAGS_FROM_FILE = get_bool_env('FEATURE_FLAGS_FROM_FILE', False)
FEATURE_FLAGS_FILE = get_env('FEATURE_FLAGS_FILE', 'feature_flags.json')
# or if file is not set, default is using offline mode
FEATURE_FLAGS_OFFLINE = get_bool_env('FEATURE_FLAGS_OFFLINE', True)
# default value for feature flags (if not overrided by environment or client)
FEATURE_FLAGS_DEFAULT_VALUE = False

# Strip harmful content from SVG files by default
SVG_SECURITY_CLEANUP = get_bool_env('SVG_SECURITY_CLEANUP', False)

ML_BLOCK_LOCAL_IP = get_bool_env('ML_BLOCK_LOCAL_IP', False)

RQ_LONG_JOB_TIMEOUT = int(get_env('RQ_LONG_JOB_TIMEOUT', 36000))

APP_WEBSERVER = get_env('APP_WEBSERVER', 'django')

# Provider
OAUTH_ENABLE            = get_env('OAUTH_ENABLE', '0') == '1'
OAUTH_SERVER            = get_env('OAUTH_API_BASE_URL', 'https://app.aixblock.io')

# General urls on your provider:
OAUTH_AUTHORIZATION_URL = '/oauth/authorize'   # Authorization URL
OAUTH_TOKEN_URL         = '/oauth/token'      # Access token URL
OAUTH_REFRESH_TOKEN_URL = OAUTH_TOKEN_URL  # Refresh Access token URL

# The URL of some protected resource on your oauth2 server which you have configured to serve
# json-encoded user information (containing at least an email) for the user associated
# with a given access token.
OAUTH_RESOURCE_URL = '/api/user' #'/api/v1/auth/user'

# From the configuration of your client site in the oauth2 provider
OAUTH_CLIENT_ID         = get_env('OAUTH_CLIENT_ID', '6')
OAUTH_CLIENT_SECRET     = get_env('OAUTH_CLIENT_SECRET', '')


# # From 'oauth2_login_client.urls'
OAUTH_CALLBACK_URL      = get_env('OAUTH_REDIRECT_URL', 'https://app.aixblock.io/oauth/login/callback')


# Optional permissions checking:
# Check permission based on a client site code passed in by the oauth2 server in the
# 'sites' element of the user info resource.
OAUTH_RESOURCE_CLIENT_CODE =  'clientcode' #'authorization_code'# 'client_credentials' #'clientcode'

# To periodically sync user details from auth server
# Add 'oauth2_login_client.middleware.OAuthMiddleware' to MIDDLEWARE_CLASSES
OAUTH_USER_SYNC_FREQUENCY = 3600 # seconds

# OAuth Settings
OAUTH_URL_WHITELISTS = []

OAUTH_CLIENT_NAME = 'AIxBlock Auth'

GOOGLE_OAUTH_CLIENT = {
    'client_id': get_env('GOOGLE_OAUTH2_CLIENT_ID', ''),
    'client_secret': get_env('GOOGLE_OAUTH2_CLIENT_SECRET', ''),
    'project_id': get_env('GOOGLE_OAUTH2_PROJECT_ID', '')
}

OAUTH_CLIENT = {
    'client_id': get_env('OAUTH_CLIENT_ID', ''),
    'client_secret': get_env('OAUTH_CLIENT_SECRET', ''),
    'access_token_url': get_env('OAUTH_TOKEN_URL', 'https://app.aixblock.io/o/token'),
    'authorize_url':get_env('OAUTH_AUTHORIZE_URL', 'https://app.aixblock.io/o/authorize'),
    'api_base_url': get_env('OAUTH_API_BASE_URL', 'https://app.aixblock.io'),
    'redirect_uri': get_env('OAUTH_REDIRECT_URL', 'https://app.aixblock.io/oauth/login/callback'),
    'client_kwargs': {
        # 'scope': '',
        'token_placement': 'header'
    },
    'userinfo_endpoint': '/api/user',
}

OAUTH_COOKIE_SESSION_ID = 'sso_session_id'
DOCKER_BACKEND_ENABLE = get_env('DOCKER_BACKEND_ENABLE', '0') == '1'

IMAGE_TO_SERVICE = {
    'huggingface_image_classification': 'computer_vision/image_classification',
    'huggingface_text_classification': 'nlp/text_classification',
    'huggingface_text2text': 'nlp/text2text',
    'huggingface_text_summarization': 'nlp/text_summarization',
    'huggingface_question_answering': 'nlp/question_answering',
    'huggingface_token_classification': 'nlp/token_classification',
    'huggingface_translation': 'nlp/translation',
}

IN_DOCKER = bool(os.environ.get('IN_DOCKER', True))
DOCKER_API = "tcp://172.17.0.1:4243" if IN_DOCKER else "unix://var/run/docker.sock"
NUM_GPUS = int(os.environ.get('NUM_GPUS', 1))
DEFAULT_IMAGE = os.environ.get('DEFAULT_IMAGE', 'yolov8')
ML_BACKEND_URL = os.environ.get('ML_BACKEND_URL', 'https://app.aixblock.io')
MQTT_SERVER = os.environ.get('MQTT_SERVER', 'test.mosquitto.org')
MQTT_INTERNAL_SERVER = os.environ.get('MQTT_INTERNAL_SERVER', '172.17.0.1')
MQTT_PORT = int(os.environ.get('MQTT_PORT', '1883'))
MQTT_PORT_TLS = int(os.environ.get('MQTT_PORT_TLS', '1884'))
MQTT_PORT_TCP = int(os.environ.get('MQTT_PORT_TCP', '1883'))
TOOLBAR_PREDICT_SAM = os.environ.get('TOOLBAR_PREDICT_SAM', 'https://app.aixblock.io:32768/toolbar_predict_sam')
TOOLBAR_PREDICT_RECTANGLE = os.environ.get('TOOLBAR_PREDICT_RECTANGLE', 'https://app.aixblock.io:32768/toolbar_predict_sam')
TOOLBAR_PREDICT_POLYGON = os.environ.get('TOOLBAR_PREDICT_POLYGON', 'https://app.aixblock.io:32768/toolbar_predict_sam')

AIXBLOCK_IMAGE_NAME = os.environ.get("AIXBLOCK_IMAGE_NAME", "aixblock/platform")
AIXBLOCK_IMAGE_VERSION = os.environ.get('AIXBLOCK_IMAGE_VERSION', 'latest')
VAST_AI_API_KEY = os.environ.get("VAST_AI_API_KEY", "")

EXABIT_USERNAME = os.environ.get("EXABIT_USERNAME", "")
EXABIT_PASSWORD = os.environ.get("EXABIT_PASSWORD", "")
EXABIT_API_KEY = os.environ.get("EXABIT_API_KEY", "")

NOTEBOOK_URL = os.environ.get('NOTEBOOK_URL', None)
NOTEBOOK_TOKEN = os.environ.get('NOTEBOOK_TOKEN', '')

NOTION_API_TOKEN = os.environ.get('NOTION_API_TOKEN', '')
OAUTH2_PROVIDER = {
    "PKCE_REQUIRED": False,
    "ACCESS_TOKEN_EXPIRE_SECONDS": 86400 * 7,
    "AUTHORIZATION_CODE_EXPIRE_SECONDS": 60,
}

MINIO_API_IP = os.environ.get("MINIO_API_IP", "")
MINIO_API_URL = os.environ.get("MINIO_API_URL", "")
MINIO_USER = os.environ.get("MINIO_USER", "")
MINIO_PASSWORD = os.environ.get("MINIO_PASSWORD", "")
MINIO_STORAGE_USE_HTTPS=False

ASSETS_CDN = os.environ.get('ASSETS_CDN', '')
PAYPAL_ENDPOINT = os.environ.get('PAYPAL_ENDPOINT', '')
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', '')
JENKINS_KEY = os.environ.get(
    "JENKINS_KEY", ""
)

JENKINS_TOKEN = os.environ.get("JENKINS_TOKEN", "")
JENKINS_URL = os.environ.get("JENKINS_URL", "")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "")
SERVICE_FEE = os.environ.get("SERVICE_FEE", "4")
AIXBLOCK_IMAGE_NAME = os.environ.get("AIXBLOCK_IMAGE_NAME","aixblock/platform")
AXB_PUBLIC_SSL_PORT = os.environ.get("AXB_PUBLIC_SSL_PORT", 8443)

CENTRIFUGE_SECRET = os.environ.get("CENTRIFUGE_SECRET", "")
CENTRIFUGE_URL = os.environ.get(
    "CENTRIFUGE_URL", "wss://rt.aixblock.io/centrifugo/connection/websocket"
)
GRAFANA_PROMETHUS =os.environ.get("GRAFANA_PROMETHUS","")
CENTRIFUGE_API = os.environ.get("CENTRIFUGE_API", "")
CENTRIFUGE_API_KEY = os.environ.get("CENTRIFUGE_API_KEY", "")
CENTRIFUGE_TOPIC_PREFIX = os.environ.get("CENTRIFUGE_TOPIC_PREFIX", "")

HOST_JUPYTERHUB = os.environ.get('HOST_JUPYTERHUB',  "http://207.246.109.178:8100")
MAIL_SERVER = os.environ.get('MAIL_SERVER', '207.246.109.178')
ADMIN_JUPYTERHUB_TOKEN = os.environ.get('ADMIN_JUPYTERHUB_TOKEN',  '')

if CENTRIFUGE_TOPIC_PREFIX == "":
    if HOSTNAME == "":
        CENTRIFUGE_TOPIC_PREFIX = "prefix/"
    else:
        hostname_hash = str(hex(binascii.crc32(HOSTNAME.encode("utf-8"))))
        CENTRIFUGE_TOPIC_PREFIX = (hostname_hash[0:16] if len(hostname_hash) > 16 else hostname_hash) + "/"

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@test.com")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

API_VERIFY_JOB = os.environ.get("API_VERIFY_JOB", "http://207.246.109.178:6000/add-compute")

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")
STRIPE_PAYMENT_METHODS_CONFIG = os.environ.get("STRIPE_PAYMENT_METHODS_CONFIG", "")

stripe.api_key = STRIPE_SECRET_KEY

GTAGS_ID = os.environ.get("GTAGS_ID")
ZOOKEEPER = os.environ.get("ZOOKEEPER")
AUDIT_TOKEN = os.environ.get("AUDIT_TOKEN")
AUDIT_LOGS = os.environ.get("AUDIT_LOGS")
THREADS_MANAGER_WORKER = int(os.environ.get("THREADS_MANAGER_WORKER", 4))

EXABBIT_SHOW = get_bool_env("EXABBIT_SHOW", False)

UPLOAD_TEMP_DIR = get_env("UPLOAD_TEMP_DIR", os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "temp"))
UPLOAD_TEMP_URL = get_env("UPLOAD_TEMP_URL", "/temp/")
UPLOAD_TEMP_DELETE_KEY = get_env("UPLOAD_TEMP_DELETE_KEY", "")
UPLOAD_TEMP_DELETE_TOKEN = get_env("UPLOAD_TEMP_DELETE_TOKEN", "")

REGISTER_TOPUP = int(os.environ.get('REGISTER_TOPUP', '0'))
X_FRAME_OPTIONS = "SAMEORIGIN"

DB_PREFIX = "axb_"
WORKFLOW_ENDPOINT=os.environ.get("WORKFLOW_ENDPOINT")
WORKFLOW_ENCRYPTION_KEY=os.environ.get("WORKFLOW_ENCRYPTION_KEY")
