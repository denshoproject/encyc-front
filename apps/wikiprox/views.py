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

from wikiprox import parse_mediawiki_title, parse_mediawiki_text, parse_mediawiki_cite_page
from wikiprox import mw_page_is_published, mw_page_lastmod
from wikiprox import encyclopedia


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
    # basic page context
    title = parse_mediawiki_title(r.text)
    bodycontent,sources = parse_mediawiki_text(r.text)
    context = {
        'title': title,
        'bodycontent': bodycontent,
        'sources': sources,
        'lastmod': mw_page_lastmod(r.text),
        }
    # author page
    if encyclopedia.is_author(title):
        template_name = 'wikiprox/author.html'
        context.update({
            'author_articles': encyclopedia.author_articles(title),
            })
    # article
    elif encyclopedia.is_article(title):
        if printer:
            template_name = 'wikiprox/article-print.html'
        else:
            template_name = 'wikiprox/article.html'
        context.update({
            'page_categories': encyclopedia.page_categories(title),
            'prev_page': encyclopedia.article_prev(title),
            'next_page': encyclopedia.article_next(title),
            })
    # retsu go!
    return render_to_response(
        template_name, context,
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def page_cite(request, page=None, template_name='wikiprox/cite.html'):
    url = '%s?title=Special:Cite&page=%s' % (settings.WIKIPROX_MEDIAWIKI_HTML, page)
    r = requests.get(url)
    if r.status_code != 200:
        return render_to_response(
            'wikiprox/404.html',
            {'title': page,},
            context_instance=RequestContext(request)
        )
    title = parse_mediawiki_title(r.text)
    return render_to_response(
        template_name,
        {'title': title,
         'bodycontent': parse_mediawiki_cite_page(r.text, page, request),},
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
        {'articles': encyclopedia.articles_a_z(),},
        context_instance=RequestContext(request)
    )

def categories(request, template_name='wikiprox/categories.html'):
    articles_by_category = []
    categories,titles_by_category = encyclopedia.articles_by_category()
    for category in categories:
        articles_by_category.append( (category,titles_by_category[category]) )
    return render_to_response(
        template_name,
        {'articles_by_category': articles_by_category,},
        context_instance=RequestContext(request)
    )
