"""
See http://www.b-list.org/weblog/2006/jun/14/django-tips-template-context-processors/
"""
from datetime import datetime
import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

def sitewide(request):
    """Variables that need to be inserted into all templates.
    """
    return {
        #'request': request,
        'debug': settings.DEBUG,
        'time': datetime.now().isoformat(),
        'pid': os.getpid(),
        'host': os.uname()[1],
        'git_commit': settings.GIT_COMMIT[:10],
        'git_branch': settings.GIT_BRANCH,
        'version': settings.VERSION,
        'packages': settings.PACKAGES,
        'docstore_hosts': settings.DOCSTORE_HOSTS[0]['host'],
        'docstore_hosts': settings.DOCSTORE_HOSTS,
        'docstore_index': settings.DOCSTORE_INDEX,
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
        'MEDIAWIKI_DEFAULT_PAGE': settings.MEDIAWIKI_DEFAULT_PAGE,
        'GOOGLE_CUSTOM_SEARCH_PASSWORD': settings.GOOGLE_CUSTOM_SEARCH_PASSWORD,
        'site_msg_text': settings.SITE_MSG_TEXT,
        }
