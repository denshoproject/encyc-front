import json

import requests

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_http_methods

from wikiprox import ddr
from wikiprox.models import Elasticsearch as Backend
from wikiprox.models import Page, Source, Author, Citation
from wikiprox.models import NotFoundError


@require_http_methods(['GET',])
def index(request, template_name='index.html'):
    return render_to_response(
        template_name,
        {},
        context_instance=RequestContext(request)
    )

def categories(request, template_name='wikiprox/categories.html'):
    return render_to_response(
        template_name,
        {
            'articles_by_category': Page.pages_by_category(),
        },
        context_instance=RequestContext(request)
    )

def contents(request, template_name='wikiprox/contents.html'):
    return render_to_response(
        template_name,
        {
            'articles': Page.pages(),
        },
        context_instance=RequestContext(request)
    )

def authors(request, template_name='wikiprox/authors.html'):
    return render_to_response(
        template_name,
        {
            'authors': Author.authors(num_columns=4),
        },
        context_instance=RequestContext(request)
    )

def author(request, url_title, template_name='wikiprox/author.html'):
    try:
        author = Author.get(url_title)
        author.scrub()
    except NotFoundError:
        raise Http404
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
    try:
        page = Page.get(url_title)
        page.scrub()
    except NotFoundError:
        page = None
    if not page:
        try:
            page = Page.get(alt_title)
            page.scrub()
        except NotFoundError:
            page = None
    if not page:
        # might be an author
        author_titles = [author.title for author in Author.authors()]
        if url_title in author_titles:
            return HttpResponseRedirect(reverse('wikiprox-author', args=[url_title]))
        elif alt_title in author_titles:
            return HttpResponseRedirect(reverse('wikiprox-author', args=[alt_title]))
        raise Http404
    
    if (not page.published) and (not settings.MEDIAWIKI_SHOW_UNPUBLISHED):
        template_name = 'wikiprox/unpublished.html'
    elif printed:
        template_name = 'wikiprox/article-print.html'
    else:
        template_name = 'wikiprox/article.html'
    # DDR objects
    # show small number of objects, distributed among topics
    TOTAL_OBJECTS = 10
    PAGE_OBJECTS = 8
    terms_objects = page.ddr_terms_objects(size=TOTAL_OBJECTS)
    ddr_objects = ddr.distribute_list(
        terms_objects,
        PAGE_OBJECTS
    )
    ddr_objects_width = 280
    ddr_img_width = ddr_objects_width / (PAGE_OBJECTS / 2)
    return render_to_response(
        template_name,
        {
            'page': page,
            'ddr_objects': ddr_objects,
            'ddr_objects_width': ddr_objects_width,
            'ddr_img_width': ddr_img_width,
            'DDR_MEDIA_URL': settings.DDR_MEDIA_URL,
        },
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def source(request, encyclopedia_id, template_name='wikiprox/source.html'):
    try:
        source = Source.get(encyclopedia_id)
    except NotFoundError:
        raise Http404
    return render_to_response(
        template_name,
        {
            'source': source,
            'rtmp_streamer': settings.RTMP_STREAMER,
        },
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def page_cite(request, url_title, template_name='wikiprox/cite.html'):
    try:
        page = Page.get(url_title)
    except NotFoundError:
        raise Http404
    if (not page.published) and (not settings.MEDIAWIKI_SHOW_UNPUBLISHED):
        raise Http404
    citation = Citation(page, request)
    return render_to_response(
        template_name,
        {
            'citation': citation,
        },
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def source_cite(request, encyclopedia_id, template_name='wikiprox/cite.html'):
    try:
        source = Source.get(encyclopedia_id)
    except NotFoundError:
        raise Http404
    citation = Citation(source, request)
    return render_to_response(
        template_name,
        {
            'citation': citation,
        },
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def related_ddr(request, url_title='index', template_name='wikiprox/related-ddr.html'):
    """List of topic terms and DDR objects relating to page
    """
    try:
        page = Page.get(url_title)
    except NotFoundError:
        raise Http404
    # Don't show <ul> list of topics (with links) at top
    # unless there are more than one
    page_topics = [
        term
        for term in page.ddr_terms_objects()
        if term['objects']
    ]
    show_topics_ul = len(page_topics) - 1
    # show small number of objects, distributed among topics
    TOTAL_OBJECTS = 10
    terms_objects = page.ddr_terms_objects(size=TOTAL_OBJECTS)
    ddr_terms_objects = ddr.distribute_dict(
        terms_objects,
        TOTAL_OBJECTS
    )
    return render_to_response(
        template_name,
        {
            'page': page,
            'ddr_terms_objects': ddr_terms_objects,
            'show_topics_ul': show_topics_ul,
            'DDR_MEDIA_URL': settings.DDR_MEDIA_URL,
        },
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def media(request, filename, template_name='wikiprox/mediafile.html'):
    """
    """
    mediafile = None
    url = '%s/imagefile/?uri=tansu/%s' % (settings.SOURCES_API, filename)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code != 200:
        assert False
    response = json.loads(r.text)
    if response and (response['meta']['total_count'] == 1):
        mediafile = response['objects'][0]
    return render_to_response(
        template_name,
        {
            'media_url': settings.SOURCES_MEDIA_URL,
            'mediafile': mediafile,
        },
        context_instance=RequestContext(request)
    )
