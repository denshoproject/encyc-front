from datetime import datetime, timedelta
import json
import re

from bs4 import BeautifulSoup, SoupStrainer
from bs4 import Comment
import requests

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.http import require_http_methods

from wikiprox import parse_mediawiki_title, parse_mediawiki_text


@require_http_methods(['GET',])
def page(request, page, template_name='wikiprox/page.html'):
    """
    Alternatives to BeautifulSoup:
    - basic string-split
    - regex
    """
    url = '%s/%s' % (settings.WIKIPROX_MEDIAWIKI_HTML, page)
    r = requests.get(url)
    if r.status_code != 200:
        assert False
    return render_to_response(
        template_name,
        {'title': parse_mediawiki_title(r.text),
         'bodycontent': parse_mediawiki_text(r.text),},
        context_instance=RequestContext(request)
    )


@require_http_methods(['GET',])
def media(request, filename, template_name='wikiprox/mediafile.html'):
    """
    """
    mediafile = None
    url = '%s/imagefile/?uri=tansu/%s' % (settings.TANSU_API, filename)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code != 200:
        assert False
    response = json.loads(r.text)
    if response and (response['meta']['total_count'] == 1):
        mediafile = response['objects'][0]
    return render_to_response(
        template_name,
        {'mediafile': mediafile,
         'media_url': settings.TANSU_MEDIA_URL,},
        context_instance=RequestContext(request)
    )


@require_http_methods(['GET',])
def index(request):
    pass
