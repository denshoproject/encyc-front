"""
See http://www.b-list.org/weblog/2006/jun/14/django-tips-template-context-processors/
"""
from datetime import datetime
import os

from django.conf import settings
from django.urls import reverse

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
        'docstore_host': settings.DOCSTORE_HOST,
        'encycfront_cluster': settings.DOCSTORE_CLUSTER,
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_URL_LOCAL_NETLOC': settings.MEDIA_URL_LOCAL_NETLOC,
        'MEDIA_URL_LOCAL_IP': settings.MEDIA_URL_LOCAL_IP,
        'STATIC_URL': settings.STATIC_URL,
        'BOOTSTRAP_URL': settings.BOOTSTRAP_URL,
        'MEDIAWIKI_DEFAULT_PAGE': settings.MEDIAWIKI_DEFAULT_PAGE,
        'GOOGLE_CUSTOM_SEARCH_PASSWORD': settings.GOOGLE_CUSTOM_SEARCH_PASSWORD,
        'site_msg_text': settings.SITE_MSG_TEXT,
        }
