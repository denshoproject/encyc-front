"""
Django settings for encyc-front project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import ConfigParser
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# User-configurable settings are located in the following files.
# Files appearing *later* in the list override earlier files.
CONFIG_FILES = [
    '/etc/encyc/production.cfg',
    '/etc/encyc/local.cfg'
]
config = ConfigParser.ConfigParser()
configs_read = config.read(CONFIG_FILES)
if not configs_read:
    raise Exception('No config file!')

# ----------------------------------------------------------------------

DEBUG = config.get('debug', 'debug')
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = config.get('debug', 'thumbnail')

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    host.strip()
    for host in config.get('security', 'allowed_hosts').strip().split(',')
]

STATIC_URL = config.get('media', 'static_url')
MEDIA_URL = config.get('media', 'media_url')
MEDIA_URL_LOCAL = config.get('media', 'media_url_local')

# elasticsearch
DOCSTORE_HOSTS = []
for node in config.get('elasticsearch', 'hosts').strip().split(','):
    host,port = node.strip().split(':')
    DOCSTORE_HOSTS.append(
        {'host':host, 'port':port}
    )
DOCSTORE_INDEX = config.get('elasticsearch', 'index')

# mediawiki
MEDIAWIKI_HTML = 'http://dango.densho.org:9066/mediawiki/index.php'
MEDIAWIKI_API  = config.get('mediawiki', 'api_url')
MEDIAWIKI_API_USERNAME = config.get('mediawiki', 'api_username')
MEDIAWIKI_API_PASSWORD = config.get('mediawiki', 'api_password')
MEDIAWIKI_API_TIMEOUT = config.get('mediawiki', 'api_timeout')
MEDIAWIKI_DEFAULT_PAGE = 'Encyclopedia'
MEDIAWIKI_TITLE = ' - Densho Encyclopedia'
MEDIAWIKI_SHOW_UNPUBLISHED = False
MEDIAWIKI_HIDDEN_CATEGORIES = (
    'Articles_Needing_Primary_Source_Video',
    'CAL60',
    'In_Camp',
    'NeedMoreInfo',
    'Status_2',
    'Status_3',
)

# primary sources / psms
SOURCES_API  = config.get('sources', 'api_url')
SOURCES_MEDIA_URL = config.get('sources', 'media_url')
SOURCES_MEDIA_URL_LOCAL  = config.get('sources', 'media_url_local')
SOURCES_MEDIA_URL_LOCAL_MARKER = config.get('sources', 'media_url_local_marker')
SOURCES_MEDIA_BUCKET = config.get('sources', 'media_bucket')
RTMP_STREAMER = config.get('sources', 'rtmp_streamer')

# ddr
DDR_TOPICS_SRC_URL = config.get('ddr', 'topics_src_url')
DDR_TOPICS_BASE = config.get('ddr', 'topics_base')
DDR_API = config.get('ddr', 'api_url')
DDR_MEDIA_URL = config.get('ddr', 'media_url')
DDR_MEDIA_URL_LOCAL = config.get('ddr', 'media_url_local')
DDR_MEDIA_URL_LOCAL_MARKER = config.get('ddr', 'media_url_local_marker')

# search
GOOGLE_CUSTOM_SEARCH_PASSWORD = config.get('search', 'google_custom_search_password')

DANGO_HTPASSWD_USER = 'TODO'
DANGO_HTPASSWD_PWD  = 'TODO'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config.get('email', 'host')
EMAIL_PORT = config.get('email', 'port')
EMAIL_USE_TLS = config.get('email', 'use_tls')
EMAIL_HOST_USER = config.get('email', 'host_user')
EMAIL_HOST_PASSWORD = config.get('email', 'host_password')
EMAIL_SUBJECT_PREFIX = '[front] '
SERVER_EMAIL = 'front@densho.org'

# ----------------------------------------------------------------------

STAGE = False

SITE_ID = 1
SECRET_KEY = config.get('security', 'secret_key')

ADMINS = (
    ('Geoff Froh', 'geoff.froh@densho.us'),
    ('geoffrey jost', 'geoffrey.jost@densho.us'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/var/lib/encyc/front.db',
    }
}

CACHES = {
    "default": {
#        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379:0",
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
        }
    }
}

# whole-site caching
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 60 * 15
CACHE_MIDDLEWARE_KEY_PREFIX = 'front'
# low-level caching
CACHE_TIMEOUT = 60 * 5

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
MEDIA_ROOT = '/var/www/html/front/media/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates/'),
    os.path.join(BASE_DIR, 'wikiprox/templates/'),
)

INSTALLED_APPS = (
    #'django.contrib.admin',
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    #'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #
    'rest_framework',
    'sorl.thumbnail',
    #
    'events',
    'locations',
    'wikiprox',
)

# sorl-thumbnail
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.cached_db_kvstore.KVStore'
THUMBNAIL_ENGINE = 'sorl.thumbnail.engines.convert_engine.Engine'
THUMBNAIL_CONVERT = 'convert'
THUMBNAIL_IDENTIFY = 'identify'
THUMBNAIL_COLORSPACE = 'sRGB'
THUMBNAIL_OPTIONS = ''
THUMBNAIL_CACHE_TIMEOUT = 60*60*24*365*10  # 10 years
THUMBNAIL_DUMMY = False
THUMBNAIL_URL_TIMEOUT = 60  # 1min

#STATICFILES_FINDERS = (
#    'django.contrib.staticfiles.finders.FileSystemFinder',
#    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
##    'django.contrib.staticfiles.finders.DefaultStorageFinder',
#)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'context_processors.sitewide',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'front.urls'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)-8s [%(module)s.%(funcName)s]  %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)-8s %(message)s'
        },
    },
    'filters': {
        # only log when settings.DEBUG == False
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/var/log/encyc/front.log',
            'when': 'D',
            'backupCount': 14,
            'filters': [],
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'level': 'ERROR',
            'propagate': True,
            'handlers': ['mail_admins'],
        },
    },
    # This is the only way I found to write log entries from the whole DDR stack.
    'root': {
        'level': 'DEBUG',
        'handlers': ['file'],
    },
}

TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'
USE_I18N = False
USE_L10N = False
