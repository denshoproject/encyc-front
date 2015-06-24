"""Encyclopedia models using Elasticsearch-DSL


TODO "Article(s)" is often used to mean "Page(s)".


See wikiprox/management/commands/encycpudate.py

# Delete and recreate index
$ python manage.py encycupdate --reset

# Update authors
$ python manage.py encycupdate --authors

# Update articles
$ python manage.py encycupdate --articles

Example usage:

>>> from elasticsearch_dsl import Index
>>> from elasticsearch_dsl.connections import connections
>>> from django.conf import settings
>>> from wikiprox.models import Elasticsearch, Author, Page, Source
>>> connections.create_connection(hosts=settings.DOCSTORE_HOSTS)
>>> index = Index(settings.DOCSTORE_INDEX)
>>> authors = [author for author in Author.authors()]
>>> pages = [page for page in Page.pages()]
>>> sources = [source for source in Source.search().execute()]
"""

from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)
import os

from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Index
from elasticsearch_dsl import DocType, String, Date, Nested, Boolean, analysis
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
import requests

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models

from wikiprox import citations
from wikiprox import ddr
from wikiprox import docstore
from wikiprox import encyclopedia
from wikiprox import mediawiki
from wikiprox import sources
from wikiprox.models.legacy import Proxy

if not settings.DEBUG:
    from bs4 import BeautifulSoup
    from wikiprox.mediawiki import remove_status_markers

MAX_SIZE = 10000

# set default hosts and index
connections.create_connection(hosts=settings.DOCSTORE_HOSTS)
index = Index(settings.DOCSTORE_INDEX)


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


class Author(DocType):
    """
    IMPORTANT: uses Elasticsearch-DSL, not the Django ORM.
    """
    url_title = String(index='not_analyzed')  # Elasticsearch id
    public = Boolean()
    published = Boolean()
    modified = Date()
    mw_api_url = String(index='not_analyzed')
    title_sort = String(index='not_analyzed')
    title = String()
    body = String()
    article_titles = String(index='not_analyzed', multi=True)
    
    class Meta:
        index = settings.DOCSTORE_INDEX
        doc_type = 'authors'
    
    def __repr__(self):
        return "<Author '%s'>" % self.url_title
    
    def __str__(self):
        return self.title

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
        TIMEOUT = 60*5
        data = cache.get(KEY)
        if not data:
            s = Search(doc_type='authors')[0:MAX_SIZE]
            s = s.sort('title_sort')
            s = s.fields([
                'url_title',
                'title',
                'title_sort',
                'published',
            ])
            response = s.execute()
            data = [
                Author(
                    url_title  = hitvalue(hit, 'url_title'),
                    title      = hitvalue(hit, 'title'),
                    title_sort = hitvalue(hit, 'title_sort'),
                    published  = hitvalue(hit, 'published'),
                )
                for hit in response
                if hitvalue(hit, 'published')
            ]
            cache.set(KEY, data, TIMEOUT)
        if num_columns:
            return _columnizer(data, num_columns)
        return data

    def scrub(self):
        """Removes internal editorial markers.
        Must be run on a full (non-list) Page object.
        TODO Should this happen upon import from MediaWiki?
        """
        if (not settings.DEBUG) and hasattr(self,'body') and self.body:
            self.body = unicode(remove_status_markers(BeautifulSoup(self.body)))

    @staticmethod
    def from_mw(mwauthor):
        """Creates an Author object from a models.legacy.Author object.
        """
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
        )
        author.article_titles = [title for title in mwauthor.author_articles]
        return author


class Page(DocType):
    """
    IMPORTANT: uses Elasticsearch-DSL, not the Django ORM.
    """
    url_title = String(index='not_analyzed')  # Elasticsearch id
    public = Boolean()
    published = Boolean()
    modified = Date()
    mw_api_url = String(index='not_analyzed')
    title_sort = String(index='not_analyzed')
    title = String()
    body = String()
    prev_page = String(index='not_analyzed')
    next_page = String(index='not_analyzed')
    categories = String(index='not_analyzed', multi=True)
    coordinates = String(index='not_analyzed', multi=True)
    source_ids = String(index='not_analyzed', multi=True)
    authors_data = Nested(
        properties={
            'display': String(index='not_analyzed', multi=True),
            'parsed': String(index='not_analyzed', multi=True),
        }
    )
    
    class Meta:
        index = settings.DOCSTORE_INDEX
        doc_type = 'articles'
    
    def __repr__(self):
        return "<Page '%s'>" % self.url_title
    
    def __str__(self):
        return self.url_title
    
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
        KEY = 'encyc-front:pages'
        TIMEOUT = 60*5
        data = cache.get(KEY)
        if not data:
            s = Search(doc_type='articles')[0:MAX_SIZE]
            s = s.sort('title_sort')
            s = s.fields([
                'url_title',
                'title',
                'title_sort',
                'published',
                'categories',
            ])
            response = s.execute()
            data = [
                Page(
                    url_title  = hitvalue(hit, 'url_title'),
                    title      = hitvalue(hit, 'title'),
                    title_sort = hitvalue(hit, 'title_sort'),
                    published  = hitvalue(hit, 'published'),
                    categories = hit.get('categories',[]),
                   )
                for hit in response
                if hitvalue(hit, 'published')
            ]
            cache.set(KEY, data, TIMEOUT)
        return data
    
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
        return [Source.get(sid) for sid in self.source_ids]
    
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
    def from_mw(mwpage):
        """Creates an Page object from a models.legacy.Page object.
        """
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
        )
        for category in mwpage.categories:
            page.categories.append(category)
        for coord in mwpage.coordinates:
            page.coordinates.append(coord)
        for source in mwpage.sources:
            page.source_ids.append(source['encyclopedia_id'])
        page.authors_data = mwpage.authors
        return page


class Source(DocType):
    """
    IMPORTANT: uses Elasticsearch-DSL, not the Django ORM.
    """
    encyclopedia_id = String(index='not_analyzed')  # Elasticsearch id
    densho_id = String(index='not_analyzed')
    psms_id = String(index='not_analyzed')
    psms_api_uri = String(index='not_analyzed')
    institution_id = String(index='not_analyzed')
    collection_name = String(index='not_analyzed')
    created = Date()
    modified = Date()
    published = Boolean()
    creative_commons = Boolean()
    headword = String(index='not_analyzed')
    original_url = String(index='not_analyzed')
    streaming_url = String(index='not_analyzed')
    external_url = String(index='not_analyzed')
    media_format = String(index='not_analyzed')
    aspect_ratio = String(index='not_analyzed')
    original_size = String(index='not_analyzed')
    display_size = String(index='not_analyzed')
    display = String(index='not_analyzed')
    caption = String()
    caption_extended = String()
    transcript = String()
    courtesy = String(index='not_analyzed')
    filename = String(index='not_analyzed')
    img_path = String(index='not_analyzed')
    
    class Meta:
        index = settings.DOCSTORE_INDEX
        doc_type = 'sources'
    
    def __repr__(self):
        return "<Source '%s'>" % self.encyclopedia_id
    
    def __str__(self):
        return self.encyclopedia_id
    
    def absolute_url(self):
        return reverse('wikiprox-source', args=([self.encyclopedia_id]))
    
    def img_url(self):
        return os.path.join(settings.SOURCES_MEDIA_URL, self.img_path)
    
    def img_url_local(self):
        return os.path.join(settings.SOURCES_MEDIA_URL_LOCAL, self.img_path)
    
    def article(self):
        if self.headword:
            try:
                page = Page.get(self.headword)
            except NotFoundError:
                page = None
        return page

    @staticmethod
    def from_mw(mwsource):
        """Creates an Source object from a models.legacy.Source object.
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
            headword = mwsource['headword'],
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
        self.href = 'http://%s%s' % (request.META['HTTP_HOST'], self.uri)
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
    
    @staticmethod
    def index_articles(titles=[], start=0, num=1000000):
        """
        @param titles: list of url_titles to retrieve.
        @param start: int Index of list at which to start.
        @param num: int Number of articles to index, beginning at start.
        @returns: (int num posted, list Articles that could not be posted)
        """
        posted = 0
        could_not_post = []
        for n,title in enumerate(titles):
            if (posted < num) and (n > start):
                logging.debug('%s/%s %s' % (n, len(titles), title))
                mwpage = Proxy().page(title)
                if (mwpage.published or settings.MEDIAWIKI_SHOW_UNPUBLISHED):
                    page_sources = [source['encyclopedia_id'] for source in mwpage.sources]
                    for mwsource in mwpage.sources:
                        logging.debug('     %s' % mwsource['encyclopedia_id'])
                        source = Source.from_mw(mwsource)
                        source.save()
                    page = Page.from_mw(mwpage)
                    page.save()
                    posted = posted + 1
                    logging.debug('posted %s' % posted)
                else:
                    could_not_post.append(page)
        if could_not_post:
            logging.debug('Could not post these: %s' % could_not_post)
        return posted,could_not_post

    @staticmethod
    def index_author(title):
        """
        @param title: str
        """
        for n,title in enumerate(titles):
            logging.debug('%s/%s %s' % (n, len(titles), title))
            mwauthor = Proxy().page(title)
            author = Author.from_mw(mwauthor)
            author.save()

    @staticmethod
    def index_topics(json_text=None, url=settings.DDR_TOPICS_SRC_URL):
        """Upload topics.json; used for Encyc->DDR links on article pages.
        
        url = 'http://partner.densho.org/vocab/api/0.2/topics.json'
        models.Elasticsearch.index_topics(url)
        
        @param json_text: unicode Raw topics.json file text.
        @param url: URL of topics.json
        """
        if url and not json_text:
            r = requests.get(url)
            if r.status_code == 200:
                json_text = r.text
        docstore.post(
            settings.DOCSTORE_HOSTS, settings.DOCSTORE_INDEX, 'vocab',
            'topics', json.loads(json_text),
        )
    
    @staticmethod
    def articles_to_update(mw_authors, mw_articles, es_authors, es_articles):
        """Returns titles of articles to update and delete
        
        >>> mw_authors = Proxy().authors(cached_ok=False)
        >>> mw_articles = Proxy().articles_lastmod()
        >>> es_authors = Elasticsearch.authors()
        >>> es_articles = Elasticsearch.articles()
        >>> results = Elasticsearch.articles_to_update(mw_authors, mw_articles, es_authors, es_articles)
        >>> Elasticsearch.index_articles(titles=results['update'])
        >>> Elasticsearch.delete_articles(titles=results['delete'])
        
        @param mw_authors: list Output of wikiprox.models.Proxy.authors_lastmod()
        @param mw_articles: list Output of wikiprox.models.Proxy.articles_lastmod()
        @param es_authors: list Output of wikiprox.models.Elasticsearch.authors()
        @param es_articles: list Output of wikiprox.models.Elasticsearch.articles()
        @returns: (articles_update,articles_delete)
        """
        # filter out the authors
        mw_lastmods = [
            a for a in mw_articles
            if a['title'] not in mw_authors
        ]
        es_pages = [a for a in es_articles if a.title not in es_authors]
        
        mw_titles = [a['title'] for a in mw_lastmods]
        es_titles = [a.title for a in es_pages]
        
        new = [mwtitle for mwtitle in mw_titles if not mwtitle in es_titles]
        deleted = [estitle for estitle in es_titles if not estitle in mw_titles]
        
        mw = {}  # so we don't loop on every es_article
        for a in mw:
            mw[a['title']] = a['lastmod']
        updated = [
            a for a in es_articles
            if (a.title in mw.keys()) and (mw[a.title] > a.lastmod)
        ]
        return (new + updated, deleted)
    
    @staticmethod
    def authors_to_update(mw_authors, es_authors):
        """Returns titles of authors to add or delete
        
        Does not track updates because it's easy just to update them all.
        
        >>> mw_authors = Proxy().authors(cached_ok=False)
        >>> es_authors = Elasticsearch.authors()
        >>> results = Elasticsearch.articles_to_update(mw_authors, es_authors)
        >>> Elasticsearch.index_authors(titles=results['update'])
        >>> Elasticsearch.delete_authors(titles=results['delete'])
        
        @param mw_authors: list Output of wikiprox.models.Proxy.authors_lastmod()
        @param es_authors: list Output of wikiprox.models.Elasticsearch.authors()
        @returns: authors_new,authors_delete
        """
        es_author_titles = [a.title for a in es_authors]
        new = [title for title in mw_authors if title not in es_author_titles]
        delete = [title for title in es_author_titles if title not in mw_authors]
        return new,delete

    @staticmethod
    def update_all():
        """Check with Proxy source and update authors and articles.
        
        IMPORTANT: Will lock if unable to connect to MediaWiki server!
        """
        # authors
        connections.create_connection(hosts=settings.DOCSTORE_HOSTS)
        index = Index(settings.DOCSTORE_INDEX)
        mw_authors = Proxy().authors(cached_ok=False)
        es_authors = self.authors()
        authors_new,authors_delete = self.authors_to_update(mw_authors, es_authors)
        
        for n,title in enumerate(authors_delete):
            logging.debug('%s/%s %s' % (n, len(authors_delete), title))
            author = Author.get(url_title=title)
            author.delete()
            
        for n,title in enumerate(authors_new):
            logging.debug('%s/%s %s' % (n, len(authors_new), title))
            mwauthor = Proxy().page(title)
            author = Author.from_mw(mwauthor)
            author.save()
        
        # articles
        connections.create_connection(hosts=settings.DOCSTORE_HOSTS)
        index = Index(settings.DOCSTORE_INDEX)
        # authors need to be refreshed
        mw_authors = Proxy().authors(cached_ok=False)
        mw_articles = Proxy().articles_lastmod()
        es_authors = self.authors()
        es_articles = self.articles()
        articles_update,articles_delete = self.articles_to_update(
            mw_authors, mw_articles, es_authors, es_articles)
        self.delete_articles(titles=articles_delete)
        self.index_articles(titles=articles_update)
