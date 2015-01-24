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

class Wiki(object):
    """Represents a MediaWiki site
    
    NOTE: not a Django model object!
    """
    
    @staticmethod
    def authors(columnize=True):
        authors = [page['title'] for page in encyclopedia.published_authors()]
        if columnize:
            return _columnizer(authors, 4)
        return authors

    @staticmethod
    def articles_by_category():
        articles_by_category = []
        categories,titles_by_category = encyclopedia.articles_by_category()
        for category in categories:
            titles = [page['title'] for page in titles_by_category[category]]
            articles_by_category.append( (category,titles) )
        return articles_by_category
    
    @staticmethod
    def contents():
        articles = [
            {'first_letter':page['sortkey'][0].upper(), 'title':page['title']}
            for page in encyclopedia.articles_a_z()
        ]
        return articles


class Page(object):
    """Represents a MediaWiki page.
    IMPORTANT: not a Django model object!
    """
    url_title = None
    url = None
    printed = None
    status_code = None
    error = None
    public = None
    published = None
    lastmod = None
    is_article = None
    is_author = None
    title = None
    body = None
    sources = []
    categories = []
    author_articles = []
    coordinates = ()
    prev_page = None
    next_page = None
    
    def __init__(self, url_title, printed=False, request=None):
        """
        @param page: Page title from URL.
        """
        logger.debug('%s, printed=%s, request=%s' % (url_title, printed, request))
        self.url_title = url_title
        self.printed = printed
        self.url = mediawiki.page_data_url(settings.WIKIPROX_MEDIAWIKI_API, self.url_title)
        logger.debug(self.url)
        auth = (settings.DANGO_HTPASSWD_USER, settings.DANGO_HTPASSWD_PWD)
        r = requests.get(self.url, auth=auth)
        self.status_code = r.status_code
        logger.debug(self.status_code)
        pagedata = json.loads(r.text)
        self.error = pagedata.get('error', None)
        if (self.status_code == 200) and not self.error:
            self.public = False
            ## hide unpublished pages on public systems
            #self.public = request.META.get('HTTP_X_FORWARDED_FOR',False)
            # note: header is added by Nginx, should not appear when connected directly
            # to the app server.
            self.published = mediawiki.page_is_published(pagedata)
            self.lastmod = mediawiki.page_lastmod(settings.WIKIPROX_MEDIAWIKI_API, self.url_title)
            # basic page context
            self.title = pagedata['parse']['displaytitle']
            self.sources = mediawiki.find_primary_sources(
                settings.TANSU_API,
                pagedata['parse']['images'])
            self.body = mediawiki.parse_mediawiki_text(
                pagedata['parse']['text']['*'],
                self.sources,
                self.public,
                self.printed)
            # rewrite media URLs on stage
            # (external URLs not visible to Chrome on Android when connecting through SonicWall)
            if hasattr(settings, 'STAGE') and settings.STAGE and request:
                self.sources = sources.replace_source_urls(self.sources, request)
            self.is_article = encyclopedia.is_article(self.title)
            if self.is_article:
                self.categories = [
                    c['*'] for c in pagedata['parse']['categories']
                    if not c.has_key('hidden')]
                self.prev_page = encyclopedia.article_prev(self.title)
                self.next_page = encyclopedia.article_next(self.title)
                self.coordinates = mediawiki.find_databoxcamps_coordinates(pagedata['parse']['text']['*'])
            self.is_author = encyclopedia.is_author(self.title)
            if self.is_author:
                self.author_articles = encyclopedia.author_articles(self.title)
    
    def __repr__(self):
        return "<Page '%s'>" % self.url_title
    
    def __str__(self):
        return self.url_title


class Source(object):
    encyclopedia_id = None
    streaming_url = None
    rtmp_streamer = ''
    
    def __init__(self, encyclopedia_id):
        self.encyclopedia_id = encyclopedia_id
        source = sources.source(encyclopedia_id)
        for key,val in source.iteritems():
            setattr(self, key, val)
        self.id = int(source['id'])
        self.original_size = int(source['original_size'])
        self.created = datetime.strptime(source['created'], mediawiki.TS_FORMAT)
        self.modified = datetime.strptime(source['modified'], mediawiki.TS_FORMAT)
        if getattr(self, 'streaming_url', None) and ('rtmp' in self.streaming_url):
            self.streaming_url = self.streaming_url.replace(settings.RTMP_STREAMER,'')
            self.rtmp_streamer = settings.RTMP_STREAMER
    
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
    authors_apa = []
    authors_bibtex = []
    authors_chicago = []
    authors_cse = []
    authors_mhra = []
    authors_mla = []
    
    def __init__(self, url_title):
        self.page_url = mediawiki.page_data_url(settings.WIKIPROX_MEDIAWIKI_API, url_title)
        self.cite_url = '%s?format=json&action=query&prop=info&prop=revisions&titles=%s' % (
            settings.WIKIPROX_MEDIAWIKI_API, url_title)
        self.url = self.cite_url
        r = requests.get(self.cite_url)
        self.status_code = r.status_code
        pagedata = json.loads(r.text)
        self.error = pagedata.get('error', None)
        if (self.status_code == 200) and not self.error:
            keys = pagedata['query']['pages'].keys()
            if len(keys) == 1:
                pageinfo = pagedata['query']['pages'][keys[0]]
                self.title = pageinfo['title']
                timestamp = pageinfo['revisions'][0]['timestamp']
                self.lastmod = datetime.strptime(timestamp, mediawiki.TS_FORMAT)
                self.retrieved = datetime.now()
                self.uri = reverse('wikiprox-page', args=[url_title])
                # get author info
                r = requests.get(self.page_url)
                pagedata2 = json.loads(r.text)
                self.authors = mediawiki.find_author_info(pagedata2['parse']['text']['*'])
                self.authors_apa = citations.format_authors_apa(self.authors['parsed'])
                self.authors_bibtex = citations.format_authors_bibtex(self.authors['parsed'])
                self.authors_chicago = citations.format_authors_chicago(self.authors['parsed'])
                self.authors_cse = citations.format_authors_cse(self.authors['parsed'])
                self.authors_mhra = citations.format_authors_mhra(self.authors['parsed'])
                self.authors_mla = citations.format_authors_mla(self.authors['parsed'])
    
    def __repr__(self):
        return "<Citation '%s'>" % self.url_title
    
    def __str__(self):
        return self.url_title


class SourceCitation(object):
    encyclopedia_id = None
    title = None
    lastmod = None
    retrieved = None
    uri = None
    
    def __init__(self, source):
        source_dict = source.__dict__
        self.encyclopedia_id = source.encyclopedia_id
        self.title = self.encyclopedia_id
        self.lastmod = source.modified
        self.retrieved = datetime.now()
        self.uri = reverse('wikiprox-source', args=[self.encyclopedia_id])
    
    def __repr__(self):
        return "<SourceCitation '%s'>" % self.encyclopedia_id
    
    def __str__(self):
        return self.encyclopedia_id
