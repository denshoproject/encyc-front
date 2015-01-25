from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)

import requests

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from wikiprox import citations
from wikiprox import encyclopedia
from wikiprox import mediawiki
from wikiprox import sources


def _columnizer(things, cols):
    columns = []
    collen = round(len(things) / float(cols))
    col = []
    for t in things:
        col.append(t)
        if len(col) > collen:
           columns.append(col)
           col = []
    columns.append(col)
    return columns


class Author(object):
    url_title = None
    uri = None
    title = None
    title_sort = None
    body = None
    lastmod = None
    author_articles = []
    
    def __repr__(self):
        return "<Author '%s'>" % self.title
    
    def __str__(self):
        return self.title


class Page(object):
    """Represents a MediaWiki page.
    IMPORTANT: not a Django model object!
    """
    url_title = None
    url = None
    uri = None
    status_code = None
    error = None
    public = None
    published = None
    lastmod = None
    is_article = None
    is_author = None
    title_sort = None
    title = None
    body = None
    sources = []
    categories = []
    author_articles = []
    coordinates = ()
    prev_page = None
    next_page = None
    
    def __repr__(self):
        return "<Page '%s'>" % self.url_title
    
    def __str__(self):
        return self.url_title


class Source(object):
    encyclopedia_id = None
    psms_id = None
    densho_id = None
    institution_id = None
    url = None
    uri = None
    resource_uri = None
    streaming_url = None
    external_url = None
    original = None
    display = None
    thumbnail_lg = None
    thumbnail_sm = None
    media_format = None
    aspect_ratio = None
    original_size = None
    display_size = None
    title = encyclopedia_id
    collection_name = None
    headword = None
    caption = None
    caption_extended = None
    transcript = None
    courtesy = None
    creative_commons = None
    created = None
    modified = None
    published = None
    rtmp_streamer = settings.RTMP_STREAMER
    authors = {'display':[], 'parsed':[],}
    
    def __repr__(self):
        return "<Source '%s'>" % self.encyclopedia_id
    
    def __str__(self):
        return self.encyclopedia_id


class Citation(object):
    """Represents a citation for a MediaWiki page.
    IMPORTANT: not a Django model object!
    """
    url_title = None
    url = None
    page_url = None
    cite_url = None
    href = None
    status_code = None
    error = None
    title = None
    lastmod = None
    retrieved = None
    authors = []
    authors_apa = ''
    authors_bibtex = ''
    authors_chicago = ''
    authors_cse = ''
    authors_mhra = ''
    authors_mla = ''
    
    def __repr__(self):
        return "<Citation '%s'>" % self.url_title
    
    def __str__(self):
        return self.url_title
    
    def __init__(self, page):
        self.uri = page.uri
        self.title = page.title
        if getattr(page, 'lastmod', None):
            self.lastmod = page.lastmod
        elif getattr(page, 'modified', None):
            self.lastmod = page.modified
        self.retrieved = datetime.now()
        self.authors = page.authors
        self.authors_apa = citations.format_authors_apa(self.authors['parsed'])
        self.authors_bibtex = citations.format_authors_bibtex(self.authors['parsed'])
        self.authors_chicago = citations.format_authors_chicago(self.authors['parsed'])
        self.authors_cse = citations.format_authors_cse(self.authors['parsed'])
        self.authors_mhra = citations.format_authors_mhra(self.authors['parsed'])
        self.authors_mla = citations.format_authors_mla(self.authors['parsed'])


class Proxy(object):
    """Interface to back-end MediaWiki site and encyc-psms
    
    NOTE: not a Django model object!
    """
    
    def articles_by_category(self):
        articles_by_category = []
        categories,titles_by_category = encyclopedia.articles_by_category()
        for category in categories:
            titles = [page['title'] for page in titles_by_category[category]]
            articles_by_category.append( (category,titles) )
        return articles_by_category
    
    def contents(self):
        articles = [
            {'first_letter':page['sortkey'][0].upper(), 'title':page['title']}
            for page in encyclopedia.articles_a_z()
        ]
        return articles

    def authors(self, columnize=True):
        authors = [page['title'] for page in encyclopedia.published_authors()]
        if columnize:
            return _columnizer(authors, 4)
        return authors

    def page(self, url_title, request=None):
        """
        @param page: Page title from URL.
        """
        logger.debug(url_title)
        page = Page()
        page.url_title = url_title
        page.uri = reverse('wikiprox-page', args=[url_title])
        page.url = mediawiki.page_data_url(settings.WIKIPROX_MEDIAWIKI_API, page.url_title)
        logger.debug(page.url)
        auth = (settings.DANGO_HTPASSWD_USER, settings.DANGO_HTPASSWD_PWD)
        r = requests.get(page.url, auth=auth)
        page.status_code = r.status_code
        logger.debug(page.status_code)
        pagedata = json.loads(r.text)
        page.error = pagedata.get('error', None)
        if (page.status_code == 200) and not page.error:
            page.public = False
            ## hide unpublished pages on public systems
            #page.public = request.META.get('HTTP_X_FORWARDED_FOR',False)
            # note: header is added by Nginx, should not appear when connected directly
            # to the app server.
            page.published = mediawiki.page_is_published(pagedata)
            page.lastmod = mediawiki.page_lastmod(settings.WIKIPROX_MEDIAWIKI_API, page.url_title)
            # basic page context
            page.title = pagedata['parse']['displaytitle']
            page.title_sort = page.title
            for prop in pagedata['parse']['properties']:
                if prop.get('name',None) and prop['name'] and (prop['name'] == 'defaultsort'):
                    page.title_sort = prop['*']
            page.sources = mediawiki.find_primary_sources(
                settings.TANSU_API,
                pagedata['parse']['images'])
            page.body = mediawiki.parse_mediawiki_text(
                pagedata['parse']['text']['*'],
                page.sources,
                page.public,
                False)
            # rewrite media URLs on stage
            # (external URLs not visible to Chrome on Android when connecting through SonicWall)
            if hasattr(settings, 'STAGE') and settings.STAGE and request:
                page.sources = sources.replace_source_urls(page.sources, request)
            page.is_article = encyclopedia.is_article(page.title)
            if page.is_article:
                page.categories = [
                    c['*'] for c in pagedata['parse']['categories']
                    if not c.has_key('hidden')]
                page.prev_page = encyclopedia.article_prev(page.title)
                page.next_page = encyclopedia.article_next(page.title)
                page.coordinates = mediawiki.find_databoxcamps_coordinates(pagedata['parse']['text']['*'])
                page.authors = mediawiki.find_author_info(pagedata['parse']['text']['*'])
            page.is_author = encyclopedia.is_author(page.title)
            if page.is_author:
                page.author_articles = encyclopedia.author_articles(page.title)
        return page

    def source(self, encyclopedia_id):
        source = Source()
        source.encyclopedia_id = encyclopedia_id
        source.uri = reverse('wikiprox-source', args=[encyclopedia_id])
        source.title = encyclopedia_id
        data = sources.source(encyclopedia_id)
        for key,val in data.iteritems():
            setattr(source, key, val)
        source.psms_id = int(data['id'])
        source.original_size = int(data['original_size'])
        source.created = datetime.strptime(data['created'], mediawiki.TS_FORMAT)
        source.modified = datetime.strptime(data['modified'], mediawiki.TS_FORMAT)
        if getattr(source, 'streaming_url', None) and ('rtmp' in source.streaming_url):
            source.streaming_url = source.streaming_url.replace(settings.RTMP_STREAMER,'')
            source.rtmp_streamer = settings.RTMP_STREAMER
        return source

    def citation(self, page):
        return Citation(page)