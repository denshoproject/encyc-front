import json

import requests

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_http_methods

from wikiprox.models import Elasticsearch as Backend
from wikiprox import ddr


@require_http_methods(['GET',])
def index(request, template_name='index.html'):
    return render_to_response(
        template_name,
        {},
        context_instance=RequestContext(request)
    )

def categories(request, template_name='wikiprox/categories.html'):
    categories = Backend().categories()
    articles_by_category = [(key,val) for key,val in categories.iteritems()]
    return render_to_response(
        template_name,
        {
            'articles_by_category': articles_by_category,
        },
        context_instance=RequestContext(request)
    )

def contents(request, template_name='wikiprox/contents.html'):
    return render_to_response(
        template_name,
        {
            'articles': Backend().articles(),
        },
        context_instance=RequestContext(request)
    )

def authors(request, template_name='wikiprox/authors.html'):
    return render_to_response(
        template_name,
        {
            'authors': Backend().authors(num_columns=4),
        },
        context_instance=RequestContext(request)
    )

def author(request, url_title, template_name='wikiprox/author.html'):
    author = Backend().author(url_title)
    author.articles = [Backend().page(title) for title in author.author_articles]
    return render_to_response(
        template_name,
        {
            'author': author,
        },
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def article(request, url_title='index', printed=False, template_name='wikiprox/page.html'):
    """
    """
    alt_title = url_title.replace('_', ' ')
    page = Backend().page(url_title)
    if not page:
        page = Backend().page(alt_title)
    if not page:
        # might be an author
        author_titles = [author.title for author in Backend().authors()]
        if url_title in author_titles:
            return HttpResponseRedirect(reverse('wikiprox-author', args=[url_title]))
        elif alt_title in author_titles:
            return HttpResponseRedirect(reverse('wikiprox-author', args=[alt_title]))
        raise Http404
    page.sources = [
        Backend().source(encyc_id).__dict__ for encyc_id in page.sources
    ]
    page.related_ddr = Backend().related_ddr(
        [term['id'] for term in page.topics()],
        balanced=True
    )
    if (not page.published) and (not settings.WIKIPROX_SHOW_UNPUBLISHED):
        template_name = 'wikiprox/unpublished.html'
    elif page.is_author:
        template_name = 'wikiprox/author.html'
    elif page.is_article and printed:
        template_name = 'wikiprox/article-print.html'
    else:
        template_name = 'wikiprox/article.html'
    return render_to_response(
        template_name,
        {
            'page': page,
        },
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def source(request, encyclopedia_id, template_name='wikiprox/source.html'):
    source = Backend().source(encyclopedia_id)
    if not source:
        raise Http404
    return render_to_response(
        template_name,
        {
            'source': source,
            'SOURCES_BASE': settings.SOURCES_BASE,
            'rtmp_streamer': settings.RTMP_STREAMER,
        },
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def page_cite(request, url_title, template_name='wikiprox/cite.html'):
    page = Backend().page(url_title)
    if page.error or page.is_author:
        raise Http404
    if (not page.published) and (not settings.WIKIPROX_SHOW_UNPUBLISHED):
        raise Http404
    citation = Backend().citation(page)
    citation.href = 'http://%s%s' % (request.META['HTTP_HOST'], citation.uri)
    return render_to_response(
        template_name,
        {
            'citation': citation,
        },
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def source_cite(request, encyclopedia_id, template_name='wikiprox/cite.html'):
    source = Backend().source(encyclopedia_id)
    if not source:
        raise Http404
    citation = Backend().citation(source)
    citation.href = 'http://%s%s' % (request.META['HTTP_HOST'], citation.uri)
    return render_to_response(
        template_name,
        {
            'citation': citation,
        },
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def related_ddr(request, url_title='index', template_name='wikiprox/related-ddr.html'):
    """
    """
    alt_title = url_title.replace('_', ' ')
    page = Backend().page(url_title)
    if not page:
        page = Backend().page(alt_title)
    
    related = Backend().related_ddr(
        [term['id'] for term in page.topics()]
    )
    page.related_ddr = []
    for term in page.topics():
        term['documents'] = related[term['id']]
        page.related_ddr.append(term)
    
    return render_to_response(
        template_name,
        {
            'page': page,
        },
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
        {
            'media_url': settings.TANSU_MEDIA_URL,
            'mediafile': mediafile,
        },
        context_instance=RequestContext(request)
    )
