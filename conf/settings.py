"""
Django settings for encyc-front project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import configparser
import os
import subprocess
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(BASE_DIR, '..', 'VERSION'), 'r') as f:
    VERSION = f.read().strip()

# User-configurable settings are located in the following files.
# Files appearing *later* in the list override earlier files.
CONFIG_FILES = [
    '/etc/encyc/front.cfg',
    '/etc/encyc/front-local.cfg'
]
config = configparser.ConfigParser()
configs_read = config.read(CONFIG_FILES)
if not configs_read:
    raise Exception('No config file!')

# ----------------------------------------------------------------------

DEBUG = config.getboolean('debug', 'debug')
GITPKG_DEBUG = config.getboolean('debug', 'gitpkg_debug')
THUMBNAIL_DEBUG = config.getboolean('debug', 'thumbnail')

if GITPKG_DEBUG:
    # report Git branch and commit
    # This branch is the one with the leading '* '.
    #try:
    GIT_BRANCH = [
        b.decode().replace('*','').strip()
        for b in subprocess.check_output(['git', 'branch']).splitlines()
        if '*' in b.decode()
       ][0]
    #except:
    #    GIT_BRANCH = 'unknown'
    #try:
        # $ git log --pretty=oneline
        # a21740293f... COMMIT MESSAGE
    
    GIT_COMMIT = subprocess.check_output([
        'git','log','--pretty=oneline','-1'
       ]).decode().strip().split(' ')[0]
    #except:
    #    GIT_COMMIT = 'unknown'
     
    def package_debs(package, apt_cache_dir='/var/cache/apt/archives'):
        """
        @param package: str Package name
        @param apt_cache_dir: str Absolute path
        @returns: list of .deb files matching package and version
        """
        cmd = 'dpkg --status %s' % package
        try:
            dpkg_raw = subprocess.check_output(cmd.split(' ')).decode()
        except subprocess.CalledProcessError:
            return ''
        data = {}
        for line in dpkg_raw.splitlines():
            if line and isinstance(line, str) and (':' in line):
                key,val = line.split(':', 1)
                data[key.strip().lower()] = val.strip()
        pkg_paths = [
            path for path in os.listdir(apt_cache_dir)
            if (package in path) and data.get('version') and (data['version'] in path)
        ]
        return pkg_paths
    
    PACKAGES = package_debs('encycrg-%s' % GIT_BRANCH)

else:
    GIT_BRANCH = []
    GIT_COMMIT = ''
    PACKAGES = []

LOG_LEVEL = config.get('debug', 'log_level')

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

THROTTLE_ANON = config.get('front', 'throttle_anon')
THROTTLE_USER = config.get('front', 'throttle_user')

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

REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_DB_CACHE = 0
REDIS_DB_SORL = 3

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "%s:%s:%s" % (REDIS_HOST, REDIS_PORT, REDIS_DB_CACHE),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                #'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wikiprox.context_processors.sitewide',
            ],
        },
    },
]

INSTALLED_APPS = (
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    #'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #
    'django_nose',
    'rest_framework',
    'sorl.thumbnail',
    #
    'front',
    'events',
    'locations',
    'wikiprox',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': THROTTLE_ANON,
        'user': THROTTLE_USER,
    },
}

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
            'class': 'logging.NullHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': LOG_LEVEL,
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
        'level': LOG_LEVEL,
        'handlers': ['file'],
    },
}

TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'
USE_I18N = False
USE_L10N = False

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
