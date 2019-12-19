from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)
import os

import requests

from elasticsearch.exceptions import NotFoundError
import elasticsearch_dsl as dsl

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models

from wikiprox import citations
from wikiprox import ddr
from wikiprox import docstore
from wikiprox import sources

if not settings.DEBUG:
    from bs4 import BeautifulSoup
    from wikiprox.mediawiki import remove_status_markers

MAX_SIZE = 10000


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

def hitvalue(hit, field):
    """
    For some reason, Search hit objects wrap values in lists.
    returns the value inside the list.
    """
    if hit.get(field) and isinstance(hit[field], list):
        value = hit[field][0]
    else:
        value = hit[field]
    return value

def none_strip(text):
    """Turn Nones into empty str, strip whitespace.
    """
    if text == None:
        text = ''
    return text.strip()

def _set_attr(obj, hit, fieldname):
    """Assign a SearchResults Hit value if present
    """
    if hasattr(hit, fieldname):
        setattr(obj, fieldname, getattr(hit, fieldname))


class Author(repo_models.Author):

    @staticmethod
    def get(title):
        ds = docstore.Docstore()
        return super(Author, Author).get(
            title, index=ds.index_name('author'), using=ds.es
    )

    def absolute_url(self):
        return reverse('wikiprox-author', args=([self.title,]))
    
    def articles(self):
        """Returns list of published light Pages for this Author.
        
        @returns: list
        """
        return [
            page
            for page in Page.pages()
            if page.url_title in self.article_titles
        ]

    @staticmethod
    def authors(num_columns=None):
        """Returns list of published light Author objects.
        
        @returns: list
        """
        searcher = search.Searcher()
        searcher.prepare(
            params={},
            search_models=[docstore.Docstore().index_name('author')],
            fields_nested=[],
            fields_agg={},
        )
        objects = sorted([
            Author.from_hit(hit)
            for hit in searcher.execute(docstore.MAX_SIZE, 0).objects
        ])
        if num_columns:
            return _columnizer(objects, num_columns)
        return objects

    @staticmethod
    def from_hit(hit):
        """Creates an Author object from a elasticsearch_dsl.response.hit.Hit.
        """
        obj = Author(
            meta={'id': hit.url_title}
        )
        _set_attr(obj, hit, 'url_title')
        _set_attr(obj, hit, 'public')
        _set_attr(obj, hit, 'published')
        _set_attr(obj, hit, 'modified')
        _set_attr(obj, hit, 'mw_api_url')
        _set_attr(obj, hit, 'title_sort')
        _set_attr(obj, hit, 'title')
        _set_attr(obj, hit, 'body')
        _set_attr(obj, hit, 'article_titles')
        return obj

    def scrub(self):
        """Removes internal editorial markers.
        Must be run on a full (non-list) Page object.
        TODO Should this happen upon import from MediaWiki?
        """
        if (not settings.DEBUG) and hasattr(self,'body') and self.body:
            self.body = unicode(remove_status_markers(BeautifulSoup(self.body)))

    @staticmethod
    def from_mw(mwauthor, author=None):
        """Creates an Author object from a models.legacy.Author object.
        """
        if author:
            author.public = mwauthor.public
            author.published = mwauthor.published
            author.modified = mwauthor.lastmod
            author.mw_api_url = mwauthor.uri
            author.title_sort = mwauthor.title_sort
            author.title = none_strip(mwauthor.title)
            author.body = none_strip(mwauthor.body)
            author.article_titles = [title for title in mwauthor.author_articles]
        else:
            author = Author(
                meta = {'id': mwauthor.url_title},
                #status_code = myauthor.status_code,
                #error = myauthor.error,
                #is_article = myauthor.is_article,
                #is_author = myauthor.is_author,
                #uri = mwauthor.uri,
                #categories = myauthor.categories,
                #sources = myauthor.sources,
                #coordinates = myauthor.coordinates,
                #authors = myauthor.authors,
                #next_path = myauthor.next_path,
                #prev_page = myauthor.prev_page,
                url_title = mwauthor.url_title,
                public = mwauthor.public,
                published = mwauthor.published,
                modified = mwauthor.lastmod,
                mw_api_url = mwauthor.uri,
                title_sort = mwauthor.title_sort,
                title = none_strip(mwauthor.title),
                body = none_strip(mwauthor.body),
                article_titles = [title for title in mwauthor.author_articles],
            )
        return author


class Page(repo_models.Page):

    @staticmethod
    def get(title):
        ds = docstore.Docstore()
        return super(Page, Page).get(
            id=title, index=ds.index_name('article'), using=ds.es
        )
    
    def absolute_url(self):
        return reverse('wikiprox-page', args=([self.title]))

    def authors(self):
        """Returns list of published light Author objects for this Page.
        
        @returns: list
        """
        objects = []
        for url_title in self.authors_data['display']:
            try:
                author = Author.get(url_title)
            except NotFoundError:
                author = url_title
            objects.append(author)
        return objects

    def first_letter(self):
        return self.title_sort[0]
    
    @staticmethod
    def pages():
        """Returns list of published light Page objects.
        
        @returns: list
        """
        searcher = search.Searcher()
        searcher.prepare(
            params={},
            search_models=[docstore.Docstore().index_name('article')],
            fields_nested=[],
            fields_agg={},
        )
        return sorted([
            Page.from_hit(hit)
            for hit in searcher.execute(docstore.MAX_SIZE, 0).objects
        ])
    
    @staticmethod
    def from_hit(hit):
        """Creates a Page object from a elasticsearch_dsl.response.hit.Hit.
        """
        obj = Page(
            meta={'id': hit.url_title}
        )
        _set_attr(obj, hit, 'url_title')
        _set_attr(obj, hit, 'public')
        _set_attr(obj, hit, 'published')
        _set_attr(obj, hit, 'published_encyc')
        _set_attr(obj, hit, 'published_rg')
        _set_attr(obj, hit, 'modified')
        _set_attr(obj, hit, 'mw_api_url')
        _set_attr(obj, hit, 'title_sort')
        _set_attr(obj, hit, 'title')
        _set_attr(obj, hit, 'description')
        _set_attr(obj, hit, 'body')
        _set_attr(obj, hit, 'authors_data')
        _set_attr(obj, hit, 'categories')
        _set_attr(obj, hit, 'coordinates')
        _set_attr(obj, hit, 'source_ids')
        return obj
    
    @staticmethod
    def pages_by_category():
        """Returns list of (category, Pages) tuples, alphabetical by category
        
        @returns: list
        """
        KEY = 'encyc-front:pages_by_category'
        TIMEOUT = 60*5
        data = cache.get(KEY)
        if not data:
            categories = {}
            for page in Page.pages():
                for category in page.categories:
                    # exclude internal editorial categories
                    if category not in settings.MEDIAWIKI_HIDDEN_CATEGORIES:
                        if category not in categories.keys():
                            categories[category] = []
                        # pages already sorted so category lists will be sorted
                        if page not in categories[category]:
                            categories[category].append(page)
            data = [
                (key,categories[key])
                for key in sorted(categories.keys())
            ]
            cache.set(KEY, data, TIMEOUT)
        return data

    def scrub(self):
        """remove internal editorial markers.
        
        Must be run on a full (non-list) Page object.
        TODO Should this happen upon import from MediaWiki?
        """
        if (not settings.DEBUG) and hasattr(self,'body') and self.body:
            self.body = unicode(remove_status_markers(BeautifulSoup(self.body)))
    
    def sources(self):
        """Returns list of published light Source objects for this Page.
        
        @returns: list
        """
        try:
            return [Source.get(sid) for sid in self.source_ids]
        except NotFoundError:
            return []
    
    def topics(self):
        """List of DDR topics associated with this page.
        
        @returns: list
        """
        # return list of dicts rather than an Elasticsearch results object
        terms = []
        for t in Elasticsearch.topics_by_url().get(self.absolute_url(), []):
            term = {
                key: val
                for key,val in t.iteritems()
            }
            term.pop('encyc_urls')
            term['ddr_topic_url'] = '%s/%s/' % (
                settings.DDR_TOPICS_BASE,
                term['id']
            )
            terms.append(term)
        return terms
    
    def ddr_terms_objects(self, size=100):
        """Get dict of DDR objects for article's DDR topic terms.
        
        Ironic: this uses DDR's REST UI rather than ES.
        """
        if not hasattr(self, '_related_terms_docs'):
            terms = self.topics()
            objects = ddr.related_by_topic(
                term_ids=[term['id'] for term in terms],
                size=size
            )
            for term in terms:
                term['objects'] = objects[term['id']]
        return terms
    
    def ddr_objects(self, size=5):
        """Get list of objects for terms from DDR.
        
        Ironic: this uses DDR's REST UI rather than ES.
        """
        objects = ddr.related_by_topic(
            term_ids=[term['id'] for term in self.topics()],
            size=size
        )
        return ddr._balance(objects, size)
    
    @staticmethod
    def from_mw(mwpage, page=None):
        """Creates an Page object from a models.legacy.Page object.
        """
        if page:
            page.public = mwpage.public
            page.published = mwpage.published
            page.modified = mwpage.lastmod
            page.mw_api_url = mwpage.url
            page.title_sort = mwpage.title_sort
            page.title = none_strip(mwpage.title)
            page.body = none_strip(mwpage.body)
            page.prev_page = mwpage.prev_page
            page.next_page = mwpage.next_page
            page.categories = [category for category in mwpage.categories]
            page.coordinates = [coord for coord in mwpage.coordinates]
            page.source_ids = [source['encyclopedia_id'] for source in mwpage.sources]
            page.authors_data = mwpage.authors
        else:
            page = Page(
                meta = {'id': mwpage.url_title},
                #status_code = mwpage.status_code,
                #error = mwpage.error,
                #is_article = mwpage.is_article,
                #is_author = mwpage.is_author,
                #uri = mwpage.uri,
                url_title = mwpage.url_title,
                public = mwpage.public,
                published = mwpage.published,
                modified = mwpage.lastmod,
                mw_api_url = mwpage.url,
                title_sort = mwpage.title_sort,
                title = none_strip(mwpage.title),
                body = none_strip(mwpage.body),
                prev_page = mwpage.prev_page,
                next_page = mwpage.next_page,
                categories = [category for category in mwpage.categories],
                coordinates = [coord for coord in mwpage.coordinates],
                source_ids = [source['encyclopedia_id'] for source in mwpage.sources],
                authors_data = mwpage.authors,
            )
        return page


class Source(repo_models.Source):

    @staticmethod
    def get(title):
        ds = docstore.Docstore()
        return super(Source, Source).get(
            title, index=ds.index_name('source'), using=ds.es
        )
    
    def absolute_url(self):
        return reverse('wikiprox-source', args=([self.encyclopedia_id]))
    
    def img_url(self):
        return os.path.join(settings.SOURCES_MEDIA_URL, self.img_path)
    
    def img_url_local(self):
        return os.path.join(settings.SOURCES_MEDIA_URL_LOCAL, self.img_path)
    
    #def streaming_url(self):
    #    return os.path.join(settings.SOURCES_MEDIA_URL, self.streaming_path)
    
    def transcript_url(self):
        if self.transcript_path():
            return os.path.join(settings.SOURCES_MEDIA_URL, self.transcript_path())
    
    def original_path(self):
        if self.original_url:
            return os.path.join(
                settings.SOURCES_MEDIA_BUCKET,
                os.path.basename(self.original_url)
            )
        return None

    def rtmp_path(self):
        return self.streaming_url
    
    def streaming_path(self):
        if self.streaming_url:
            return os.path.join(
                settings.SOURCES_MEDIA_BUCKET,
                os.path.basename(self.streaming_url)
            )
        return None
    
    def transcript_path(self):
        if self.transcript:
            return os.path.join(
                settings.SOURCES_MEDIA_BUCKET,
                os.path.basename(self.transcript)
            )
        return None
    
    def article(self):
        if self.headword:
            try:
                page = Page.get(self.headword)
            except NotFoundError:
                page = None
        return page
    
    @staticmethod
    def sources():
        """Returns list of published light Source objects.
        
        @returns: list
        """
        searcher = search.Searcher()
        searcher.prepare(
            params={},
            search_models=[docstore.Docstore().index_name('source')],
            fields_nested=[],
            fields_agg={},
        )
        return sorted([
            Source.from_hit(hit)
            for hit in searcher.execute(docstore.MAX_SIZE, 0).objects
        ])
    
    @staticmethod
    def from_hit(hit):
        """Creates a Source object from a elasticsearch_dsl.response.hit.Hit.
        """
        obj = Source(
            meta={'id': hit.encyclopedia_id}
        )
        _set_attr(obj, hit, 'encyclopedia_id')
        _set_attr(obj, hit, 'densho_id')
        _set_attr(obj, hit, 'psms_id')
        _set_attr(obj, hit, 'psms_api')
        _set_attr(obj, hit, 'institution_id')
        _set_attr(obj, hit, 'collection_name')
        _set_attr(obj, hit, 'created')
        _set_attr(obj, hit, 'modified')
        _set_attr(obj, hit, 'published')
        _set_attr(obj, hit, 'creative_commons')
        _set_attr(obj, hit, 'headword')
        _set_attr(obj, hit, 'original')
        _set_attr(obj, hit, 'original_size')
        _set_attr(obj, hit, 'original_url')
        _set_attr(obj, hit, 'original_path')
        _set_attr(obj, hit, 'original_path_abs')
        _set_attr(obj, hit, 'display')
        _set_attr(obj, hit, 'display_size')
        _set_attr(obj, hit, 'display_url')
        _set_attr(obj, hit, 'display_path')
        _set_attr(obj, hit, 'display_path_abs')
        #_set_attr(obj, hit, 'streaming_path')
        #_set_attr(obj, hit, 'rtmp_path')
        _set_attr(obj, hit, 'streaming_url')
        _set_attr(obj, hit, 'external_url')
        _set_attr(obj, hit, 'media_format')
        _set_attr(obj, hit, 'aspect_ratio')
        _set_attr(obj, hit, 'caption')
        _set_attr(obj, hit, 'caption_extended')
        #_set_attr(obj, hit, 'transcript_path')
        _set_attr(obj, hit, 'transcript')
        _set_attr(obj, hit, 'courtesy')
        _set_attr(obj, hit, 'filename')
        _set_attr(obj, hit, 'img_path')
        return obj
    
    @staticmethod
    def from_mw(mwsource, url_title):
        """Creates an Source object from a models.legacy.Source object.
        
        @param mwsource: wikiprox.models.legacy.Source
        @param url_title: str url_title of associated Page
        @returns: wikiprox.models.elastic.Source
        """
        # source.streaming_url has to be relative to RTMP_STREAMER
        # TODO this should really happen when it's coming in from MediaWiki.
        if mwsource.get('streaming_url'):
            streaming_url = mwsource['streaming_url'].replace(settings.RTMP_STREAMER, '')
        else:
            streaming_url = ''
        # fullsize image for thumbnail
        filename = ''
        img_path = ''
        if mwsource.get('display'):
            filename = os.path.basename(mwsource['display'])
            img_path = os.path.join(settings.SOURCES_MEDIA_BUCKET, filename)
        elif mwsource.get('original'):
            filename = os.path.basename(mwsource['original'])
            img_path = os.path.join(settings.SOURCES_MEDIA_BUCKET, filename)
        source = Source(
            meta = {'id': mwsource['encyclopedia_id']},
            encyclopedia_id = mwsource['encyclopedia_id'],
            densho_id = mwsource['densho_id'],
            psms_id = mwsource['id'],
            psms_api_uri = mwsource['resource_uri'],
            institution_id = mwsource['institution_id'],
            collection_name = mwsource['collection_name'],
            created = mwsource['created'],
            modified = mwsource['modified'],
            published = mwsource['published'],
            creative_commons = mwsource['creative_commons'],
            headword = url_title,
            original_url = mwsource['original'],
            streaming_url = streaming_url,
            external_url = mwsource['external_url'],
            media_format = mwsource['media_format'],
            aspect_ratio = mwsource['aspect_ratio'],
            original_size = mwsource['original_size'],
            display_size = mwsource['display_size'],
            display = mwsource['display'],
            caption = none_strip(mwsource['caption']),
            caption_extended = none_strip(mwsource['caption_extended']),
            transcript = none_strip(mwsource['transcript']),
            courtesy = none_strip(mwsource['courtesy']),
            filename = filename,
            img_path = img_path,
        )
        return source


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
    
    def __init__(self, page, request):
        self.uri = page.absolute_url()
        self.href = 'https://%s%s' % (request.META['HTTP_HOST'], self.uri)
        if getattr(page, 'title', None):
            self.title = page.title
        elif getattr(page, 'caption', None):
            self.title = page.caption
        if getattr(page, 'lastmod', None):
            self.lastmod = page.lastmod
        elif getattr(page, 'modified', None):
            self.lastmod = page.modified
        if getattr(page, 'authors_data', None):
            self.authors = page.authors_data
            self.authors_apa = citations.format_authors_apa(self.authors['parsed'])
            self.authors_bibtex = citations.format_authors_bibtex(self.authors['parsed'])
            self.authors_chicago = citations.format_authors_chicago(self.authors['parsed'])
            self.authors_cse = citations.format_authors_cse(self.authors['parsed'])
            self.authors_mhra = citations.format_authors_mhra(self.authors['parsed'])
            self.authors_mla = citations.format_authors_mla(self.authors['parsed'])
        self.retrieved = datetime.now()


class Elasticsearch(object):
    """Interface to Elasticsearch backend
    NOTE: not a Django model object!
    """

    @staticmethod
    def topics():
        terms = []
        results = docstore.get(
            settings.DOCSTORE_HOSTS, settings.DOCSTORE_INDEX, 'vocab',
            'topics'
        )
        if results and (results['_source']['terms']):
            terms = [
                {
                    'id': term['id'],
                    'title': term['title'],
                    '_title': term['_title'],
                    'encyc_urls': term['encyc_urls'],
                }
                for term in results['_source']['terms']
            ]
        return terms

    @staticmethod
    def topics_by_url():
        KEY = 'encyc-front:topics_by_url'
        TIMEOUT = 60*5
        data = cache.get(KEY)
        if not data:
            data = {}
            for term in Elasticsearch.topics():
                for url in term['encyc_urls']:
                    if not data.get(url, None):
                        data[url] = []
                    data[url].append(term)
            cache.set(KEY, data, TIMEOUT)
        return data
