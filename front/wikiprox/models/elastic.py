from collections import OrderedDict
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
from wikiprox import repo_models
from wikiprox import search
from wikiprox import sources

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
        KEY = 'encyc-front:authors'
        data = cache.get(KEY)
        if not data:
            searcher = search.Searcher()
            searcher.prepare(
                params={},
                search_models=[docstore.Docstore().index_name('author')],
                fields_nested=[],
                fields_agg={},
            )
            data = sorted([
                Author.from_hit(hit)
                for hit in searcher.execute(docstore.MAX_SIZE, 0).objects
            ])
            if num_columns:
                return _columnizer(data, num_columns)
            cache.set(KEY, data, settings.CACHE_TIMEOUT)
        return data

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


class Page(repo_models.Page):

    @staticmethod
    def get(title):
        ds = docstore.Docstore()
        page = super(Page, Page).get(
            id=title, index=ds.index_name('article'), using=ds.es
        )
        # filter out ResourceGuide items
        if not page.published_encyc:
            return None
        return page
    
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
    
    @staticmethod
    def pages():
        """Returns list of published light Page objects.
        
        @returns: list
        """
        KEY = 'encyc-front:pages'
        data = cache.get(KEY)
        if not data:
            params={
                # filter out ResourceGuide items
                'published_encyc': True,
            }
            searcher = search.Searcher()
            searcher.prepare(
                params=params,
                search_models=[docstore.Docstore().index_name('article')],
                fields_nested=[],
                fields_agg={},
            )
            data = sorted([
                Page.from_hit(hit)
                for hit in searcher.execute(docstore.MAX_SIZE, 0).objects
            ])
            cache.set(KEY, data, settings.CACHE_TIMEOUT)
        return data
    
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
            cache.set(KEY, data, settings.CACHE_TIMEOUT)
        return data

    @staticmethod
    def pages_by_initial():
        KEY = 'encyc-front:pages_by_category'
        data = cache.get(KEY)
        if not data:
            data = OrderedDict()
            data['1-10'] = []
            for c in 'abcdefghijklmnopqrstuvwxyz':
                data[c] = []
            for page in Page.pages():
                initial = page.title_sort[0].lower()
                if initial.isdigit():
                    initial = '1-10'
                data[initial].append({
                    'first_letter': page.title_sort[0].upper(),
                    'title_sort': page.title_sort,
                    'title': page.title,
                    'absolute_url': page.absolute_url(),
                })
            for initial,pages in data.items():
                data[initial] = sorted(
                    pages, key=lambda page: page['title_sort']
                )
            cache.set(KEY, data, settings.CACHE_TIMEOUT)
        return data

    @staticmethod
    def titles():
        """List of Page titles
        
        @returns: list
        """
        KEY = 'encyc-front:page-titles'
        data = cache.get(KEY)
        if not data:
            data = [page.title for page in Page.pages()]
            cache.set(KEY, data, settings.CACHE_TIMEOUT)
        return data
    
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
        for term in FacetTerm.topics_by_url().get(self.title, []):
            #term.pop('encyc_urls')
            url = '%s/%s/' % (
                settings.DDR_TOPICS_BASE,
                term['id']
            )
            setattr(term, 'ddr_topic_url', url)
            terms.append(term)
        return terms
    
    def ddr_terms_objects(self, size=100):
        """Get dict of DDR objects for article's DDR topic terms.
        
        Ironic: this uses DDR's REST UI rather than ES.
        """
        if not hasattr(self, '_related_terms_docs'):
            terms = self.topics()
            objects = ddr.related_by_topic(
                term_ids=[term.term_id for term in terms],
                size=size
            )
            for term in terms:
                term['objects'] = objects[term.term_id]
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

    def set_prev_next(self):
        """Sets and previous and next page objects
        Don't put in Page.get or lists or you'll get three pages for every one
        """
        # previous,next pages
        titles = Page.titles()
        page_index = None
        for n,title in enumerate(titles):
            if title == self.title:
                page_index = n
        try:
            self.prev_page = Page.get(titles[page_index-1])
        except:
            self.prev_page = None
        try:
            self.next_page = Page.get(titles[page_index+1])
        except:
            self.next_page = None
        return self.prev_page,self.next_page

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
        KEY = 'encyc-front:sources'
        data = cache.get(KEY)
        if not data:
            searcher = search.Searcher()
            searcher.prepare(
                params={},
                search_models=[docstore.Docstore().index_name('source')],
                fields_nested=[],
                fields_agg={},
            )
            data = sorted([
                Source.from_hit(hit)
                for hit in searcher.execute(docstore.MAX_SIZE, 0).objects
            ])
            cache.set(KEY, data, settings.CACHE_TIMEOUT)
        return data
    
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


class FacetTerm(repo_models.FacetTerm):
    """Interface to Elasticsearch backend
    NOTE: not a Django model object!
    """
    
    @staticmethod
    def from_hit(hit):
        """Creates a Source object from a elasticsearch_dsl.response.hit.Hit.
        """
        obj = FacetTerm(
            meta={'id': hit.id}
        )
        _set_attr(obj, hit, 'id')
        _set_attr(obj, hit, 'facet')
        _set_attr(obj, hit, 'term_id')
        _set_attr(obj, hit, 'links_html')
        _set_attr(obj, hit, 'links_json')
        _set_attr(obj, hit, 'links_children')
        _set_attr(obj, hit, 'title')
        _set_attr(obj, hit, 'description')
        # topics
        _set_attr(obj, hit, 'path')
        _set_attr(obj, hit, 'parent_id')
        _set_attr(obj, hit, 'ancestors')
        _set_attr(obj, hit, 'siblings')
        _set_attr(obj, hit, 'children')
        _set_attr(obj, hit, 'weight')
        _set_attr(obj, hit, 'encyc_urls')
        # facility
        _set_attr(obj, hit, 'type')
        _set_attr(obj, hit, 'elinks')
        _set_attr(obj, hit, 'location_geopoint')
        return obj

    @staticmethod
    def topics():
        searcher = search.Searcher()
        searcher.prepare(
            params={
                'facet_id': 'topics',
            },
            search_models=[docstore.Docstore().index_name('facetterm')],
            fields_nested=[],
            fields_agg={},
        )
        results = searcher.execute(docstore.MAX_SIZE, 0)
        objects = results.objects
        data = sorted([FacetTerm.from_hit(hit) for hit in objects])
        return data
    
    @staticmethod
    def topics_by_url():
        KEY = 'encyc-front:topics_by_url'
        TIMEOUT = 60*5
        data = cache.get(KEY)
        if not data:
            data = {}
            for term in FacetTerm.topics():
                if hasattr(term, 'encyc_urls') and term.encyc_urls:
                    for url in term.encyc_urls:
                        title = url['title']
                        if not data.get(title, None):
                            data[title] = []
                        data[title].append(term)
            cache.set(KEY, data, TIMEOUT)
        return data

    def articles(self):
        """Returns list of published Pages for this topic.
        
        @returns: list
        """
        return [
            page
            for page in Page.pages()
            if page.url_title in self.article_titles
        ]
