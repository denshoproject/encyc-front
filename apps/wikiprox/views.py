from datetime import datetime, timedelta
import json
import os
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
from wikiprox import mw_page_is_published, mw_page_lastmod
from wikiprox.encyclopedia import page_categories


@require_http_methods(['GET',])
def page(request, page='index', printer=False, template_name='wikiprox/page.html'):
    """
    Alternatives to BeautifulSoup:
    - basic string-split
    - regex
    """
    url = '%s/%s' % (settings.WIKIPROX_MEDIAWIKI_HTML, page)
    if request.GET.get('pagefrom', None):
        url = '?'.join([url, 'pagefrom=%s' % request.GET['pagefrom']])
    elif request.GET.get('pageuntil', None):
        url = '?'.join([url, 'pageuntil=%s' % request.GET['pageuntil']])
    # request
    r = requests.get(url)
    if r.status_code != 200:
        return render_to_response(
            'wikiprox/404.html',
            {'title': page,},
            context_instance=RequestContext(request)
        )
    # only allow unpublished pages on :8000
    if (not mw_page_is_published(r.text)) and ('8000' not in request.META.get('HTTP_HOST',None)):
        return render_to_response(
            'wikiprox/unpublished.html',
            {},
            context_instance=RequestContext(request)
        )
    return render_to_response(
        template_name,
        {'title': parse_mediawiki_title(r.text),
         'bodycontent': parse_mediawiki_text(r.text),
         'lastmod': mw_page_lastmod(r.text),
         'page_categories': page_categories(page),
         'prev_page': 'prev_page',
         'next_page': 'next_page',
         },
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def page_cite(request, page=None, template_name='wikiprox/page-cite.html'):
    return render_to_response(
        template_name,
        {},
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
def source(request, encyclopedia_id, template_name='wikiprox/source.html'):
    """
    """
    url = '%s/primarysource/?encyclopedia_id=%s' % (settings.TANSU_API, encyclopedia_id)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code != 200:
        return render_to_response(
            'wikiprox/404-source.html',
            {'filename': filename,},
            context_instance=RequestContext(request)
        )
    response = json.loads(r.text)
    if response and (response['meta']['total_count'] == 1):
        source = response['objects'][0]
    rtmp_streamer = ''
    if source.get('streaming_url',None) and ('rtmp' in source['streaming_url']):
        source['streaming_url'] = source['streaming_url'].replace(settings.RTMP_STREAMER,'')
        rtmp_streamer = settings.RTMP_STREAMER
    return render_to_response(
        template_name,
        {'source': source,
         'SOURCES_BASE': settings.SOURCES_BASE,
         'rtmp_streamer': rtmp_streamer,},
        context_instance=RequestContext(request)
    )

def contents(request, template_name='wikiprox/contents.html'):
    return render_to_response(
        template_name,
        {},
        context_instance=RequestContext(request)
    )

def categories(request, template_name='wikiprox/categories.html'):
    return render_to_response(
        template_name,
        {},
        context_instance=RequestContext(request)
    )
