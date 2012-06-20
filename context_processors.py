"""
See http://www.b-list.org/weblog/2006/jun/14/django-tips-template-context-processors/
"""
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

def sitewide(request):
    """Variables that need to be inserted into all templates.
    """
    return {
        #'request': request,
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
        'WIKIPROX_MEDIAWIKI_DEFAULT_PAGE': settings.WIKIPROX_MEDIAWIKI_DEFAULT_PAGE,
        'GOOGLE_CUSTOM_SEARCH_PASSWORD': settings.GOOGLE_CUSTOM_SEARCH_PASSWORD,
        }
