"""
Django settings for encyc-front project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# ----------------------------------------------------------------------

DEBUG = False
TEMPLATE_DEBUG = DEBUG

STAGE = False

SITE_ID = 1
SECRET_KEY = 'TODO'

ADMINS = (
    ('Geoff Froh', 'geoff.froh@densho.us'),
    ('geoffrey jost', 'geoffrey.jost@densho.us'),
)
MANAGERS = ADMINS

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'TODO'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'TODO'
EMAIL_HOST_PASSWORD = 'TODO'
EMAIL_SUBJECT_PREFIX = '[front] '
SERVER_EMAIL = 'front@densho.org'

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

STATIC_ROOT = '/usr/local/src/encyc-front/front/static/'
STATIC_URL = 'http://encyclopedia.densho.org/front/static/'
#STATIC_URL = 'http://localhost:8000/static/'

MEDIA_ROOT = '/usr/local/src/encyc-front/front/media/'
MEDIA_URL = 'http://encyclopedia.densho.org/front/media/'
#MEDIA_URL = 'http://localhost:8000/media/'

TEMPLATE_DIRS = (
    '/usr/local/src/encyc-front/front/templates/',
)

INSTALLED_APPS = (
    #'django.contrib.admin',
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    #'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.messages',
    #'django.contrib.staticfiles',
    #
    'events',
    'locations',
    'wikiprox',
)

# ----------------------------------------------------------------------

# wikiprox
WIKIPROX_MEDIAWIKI_HTML = 'http://dango.densho.org:9066/mediawiki/index.php'
#WIKIPROX_MEDIAWIKI_HTML = 'http://127.0.0.1:9000/mediawiki/index.php'
WIKIPROX_MEDIAWIKI_API  = 'http://dango:9066/mediawiki/api.php'
#WIKIPROX_MEDIAWIKI_API  = 'http://127.0.0.1:9000/mediawiki/api.php'
WIKIPROX_MEDIAWIKI_API_USERNAME = 'frontbot'
WIKIPROX_MEDIAWIKI_API_PASSWORD = 'TODO'
WIKIPROX_MEDIAWIKI_DEFAULT_PAGE = 'Encyclopedia'
WIKIPROX_MEDIAWIKI_TITLE = ' - Densho Encyclopedia'
WIKIPROX_SHOW_UNPUBLISHED = False
#EDITORS_MEDIAWIKI_USER = 'denshowiki'
#EDITORS_MEDIAWIKI_PASS = 'TODO'
TANSU_API  = 'http://dango:8080/api/v1.0'
#TANSU_API  = 'http://127.0.0.1:8080/api/v1.0'
TANSU_MEDIA_URL  = 'http://encyclopedia.densho.org/psms/media/'
#TANSU_MEDIA_URL  = 'http://192.168.0.16/psms/media/'
SOURCES_BASE = 'http://encyclopedia.densho.org/'
#SOURCES_BASE = 'http://192.168.0.16/wiki/'
RTMP_STREAMER = 'rtmp://streaming.densho.org/denshostream'

DANGO_HTPASSWD_USER = 'TODO'
DANGO_HTPASSWD_PWD  = 'TODO'

GOOGLE_CUSTOM_SEARCH_PASSWORD='TODO'

DDR_TOPICS_SRC_URL = 'http://partner.densho.org/vocab/api/0.2/topics.json'
DDR_TOPICS_BASE = 'http://ddr.densho.org/browse/topics'

DOCSTORE_HOSTS = [{
    'host':'127.0.0.1',
    'port':9200
}]
DOCSTORE_INDEX = 'encyc-production'

DDRPUBLIC_DOCSTORE_HOSTS = [{
    'host':'192.168.0.31',
    'port':9200
}]
DDRPUBLIC_DOCSTORE_INDEX = 'production'
DDRPUBLIC_DOCUMENT_URL = 'http://ddr.densho.org'
DDRPUBLIC_MEDIA_URL = 'http://ddr.densho.org/media'

# ----------------------------------------------------------------------

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
