"""Commands for updating Elasticsearch using data from MediaWiki.

Add this to `/etc/crontab`:

    SHELL=/bin/bash
    MIN *     * * *   encyc     cd /usr/local/src/encyc-front/front && /usr/local/src/env/front/bin/python manage.py encyc

"""

from datetime import datetime
import logging
logger = logging.getLogger(__name__)
from optparse import make_option
import sys

from elasticsearch_dsl import Index, DocType, String
from elasticsearch_dsl.connections import connections
from elasticsearch.exceptions import NotFoundError
import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

#from DDR import docstore
#from wikiprox import encyclopedia
from wikiprox import docstore
from wikiprox.models.legacy import Proxy
from wikiprox.models import Elasticsearch
from wikiprox.models import Author, Page, Source


def logprint(level, msg):
    print('%s %s' % (datetime.now(), msg))
    if   level == 'debug': logging.debug(msg)
    elif level == 'info': logging.info(msg)
    elif level == 'error': logging.error(msg)

def config():
    print('manage.py encyc commands will use the following settings:')
    print('')
    print('DOCSTORE_HOSTS:         %s' % settings.DOCSTORE_HOSTS)
    print('DOCSTORE_INDEX:         %s' % settings.DOCSTORE_INDEX)
    print('MEDIAWIKI_HTML:         %s' % settings.MEDIAWIKI_HTML)
    print('MEDIAWIKI_API:          %s' % settings.MEDIAWIKI_API)
    print('MEDIAWIKI_API_USERNAME: %s' % settings.MEDIAWIKI_API_USERNAME)
    print('MEDIAWIKI_API_PASSWORD: %s' % settings.MEDIAWIKI_API_PASSWORD)
    print('MEDIAWIKI_API_TIMEOUT:  %s' % settings.MEDIAWIKI_API_TIMEOUT)
    print('')

def set_hosts_index():
    logprint('debug', 'hosts: %s' % settings.DOCSTORE_HOSTS)
    connections.create_connection(hosts=settings.DOCSTORE_HOSTS)
    logprint('debug', 'index: %s' % settings.DOCSTORE_INDEX)
    index = Index(settings.DOCSTORE_INDEX)
    return index
    
def delete_index():
    index = set_hosts_index()
    logprint('debug', 'deleting old index')
    index.delete()
    logprint('debug', 'DONE')
    
def create_index():
    index = set_hosts_index()
    logprint('debug', 'creating new index')
    index = Index(settings.DOCSTORE_INDEX)
    index.create()
    logprint('debug', 'creating mappings')
    Author.init()
    Page.init()
    Source.init()
    logprint('debug', 'registering doc types')
    index.doc_type(Author)
    index.doc_type(Page)
    index.doc_type(Source)
    logprint('debug', 'DONE')

def authors(report=False, dryrun=False):
    index = set_hosts_index()

    logprint('debug', '------------------------------------------------------------------------')
    logprint('debug', 'getting mw_authors...')
    mw_authors = Proxy().authors(cached_ok=False)
    logprint('debug', 'getting es_authors...')
    es_authors = Author.authors()
    logprint('debug', 'determining new,delete...')
    authors_new,authors_delete = Elasticsearch.authors_to_update(mw_authors, es_authors)
    logprint('debug', 'mediawiki authors: %s' % len(mw_authors))
    logprint('debug', 'elasticsearch authors: %s' % len(es_authors))
    logprint('debug', 'authors to add: %s' % len(authors_new))
    logprint('debug', 'authors to delete: %s' % len(authors_delete))
    if report:
        return
    
    logprint('debug', 'deleting...')
    for n,title in enumerate(authors_delete):
        logprint('debug', '--------------------')
        logprint('debug', '%s/%s %s' % (n, len(authors_delete), title))
        author = Author.get(url_title=title)
        if not dryrun:
            author.delete()
     
    logprint('debug', 'adding...')
    for n,title in enumerate(authors_new):
        logprint('debug', '--------------------')
        logprint('debug', '%s/%s %s' % (n, len(authors_new), title))
        logprint('debug', 'getting from mediawiki')
        mwauthor = Proxy().page(title)
        logprint('debug', 'creating author')
        author = Author.from_mw(mwauthor)
        if not dryrun:
            logprint('debug', 'saving')
            author.save()
            try:
                a = Author.get(title)
            except NotFoundError:
                logprint('error', 'ERROR: Author(%s) NOT SAVED!' % title)
    
    logprint('debug', 'DONE')

def articles(report=False, dryrun=False):
    index = set_hosts_index()
    
    logprint('debug', '------------------------------------------------------------------------')
    # authors need to be refreshed
    logprint('debug', 'getting mw_authors,articles...')
    mw_authors = Proxy().authors(cached_ok=False)
    mw_articles = Proxy().articles_lastmod()
    logprint('debug', 'getting es_authors,articles...')
    es_authors = Author.authors()
    es_articles = Page.pages()
    logprint('debug', 'determining new,delete...')
    articles_update,articles_delete = Elasticsearch.articles_to_update(
        mw_authors, mw_articles, es_authors, es_articles)
    logprint('debug', 'mediawiki articles: %s' % len(mw_articles))
    logprint('debug', 'elasticsearch articles: %s' % len(es_articles))
    logprint('debug', 'articles to update: %s' % len(articles_update))
    logprint('debug', 'articles to delete: %s' % len(articles_delete))
    if report:
        return
    
    logprint('debug', 'adding articles...')
    posted = 0
    could_not_post = []
    for n,title in enumerate(articles_update):
        logprint('debug', '--------------------')
        logprint('debug', '%s/%s %s' % (n+1, len(articles_update), title))
        logprint('debug', 'getting from mediawiki')
        mwpage = Proxy().page(title)
        if (mwpage.published or settings.MEDIAWIKI_SHOW_UNPUBLISHED):
            page_sources = [source['encyclopedia_id'] for source in mwpage.sources]
            for mwsource in mwpage.sources:
                logprint('debug', '- source %s' % mwsource['encyclopedia_id'])
                source = Source.from_mw(mwsource)
                if not dryrun:
                    source.save()
            logprint('debug', 'creating page')
            page = Page.from_mw(mwpage)
            if not dryrun:
                logprint('debug', 'saving')
                page.save()
                try:
                    p = Page.get(title)
                except NotFoundError:
                    logprint('error', 'ERROR: Page(%s) NOT SAVED!' % title)
        else:
            logprint('debug', 'not publishable: %s' % mwpage)
            could_not_post.append(mwpage)
    
    if could_not_post:
        logprint('debug', '========================================================================')
        logprint('debug', 'Could not post these: %s' % could_not_post)
    logprint('debug', 'DONE')

def topics(report=False, dryrun=False):
    index = set_hosts_index()

    logprint('debug', '------------------------------------------------------------------------')
    logprint('debug', 'indexing topics...')
    Elasticsearch.index_topics()
    logprint('debug', 'DONE')


class Command(BaseCommand):
    help = 'Updates authors and articles.'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '-d', '--dryrun', action='store_const', const=1,
            help="perform a trial run with no changes made"
        )
        parser.add_argument(
            '-c', '--config', action='store_const', const=1,
            help='Print configuration settings.'
        )
        parser.add_argument(
            '-r', '--report', action='store_const', const=1,
            help='report number of MediaWiki/Elasticsearch records and number to be indexed/updated.'
        )
        parser.add_argument(
            '--create-index', action='store_const', const=1,
            help='Create new index.'
        )
        parser.add_argument(
            '--delete-index', action='store_const', const=1,
            help='Delete index (requires --confirm).'
        )
        parser.add_argument(
            '--reset-index', action='store_const', const=1,
            help='Delete existing index and create new one (requires --confirm).'
        )
        parser.add_argument(
            '--confirm', action='store_const', const=1,
            help='Confirm that you really seriously want to delete/create/reset.'
        )
        parser.add_argument(
            '-t', '--topics', action='store_const', const=1,
            help='index encyc<->DDR topics.'
        )
        parser.add_argument(
            '-a', '--authors', action='store_const', const=1,
            help='index authors.'
        )
        parser.add_argument(
            '-A', '--articles', action='store_const', const=1,
            help='index articles.'
        )
    
    def handle(self, *args, **options):

        actions = [
            'config',
            'delete_index', 'create_index', 'reset_index',
            'topics', 'authors', 'articles',
        ]
        selected = [key for key in actions if options[key]]
        if not selected:
            print('Choose an action. Try "python manage.py encyc --help".')
            sys.exit(1)
        if options['delete_index'] and not options['confirm']:
            print('*** Do you really want to delete?  All existing records will be deleted!')
            print('*** If you want to proceed, add the --confirm argument.')
            sys.exit(1)
        if options['create_index'] and not options['confirm']:
            print('*** Do you really want to make a new index?  All records will be deleted!')
            print('*** If you want to proceed, add the --confirm argument.')
            sys.exit(1)
        if options['reset_index'] and not options['confirm']:
            print('*** Do you really want to reset?  All existing records will be deleted!')
            print('*** If you want to proceed, add the --confirm argument.')
            sys.exit(1)
        
        if options['config']:
            config()
        
        if options['reset_index'] and options['confirm']:
            try:
                delete_index()
                create_index()
            except requests.exceptions.ConnectionError:
                logprint('error', 'ConnectionError: check connection to MediaWiki or Elasticsearch.')
            except requests.exceptions.ReadTimeout as e:
                logprint('error', 'ReadTimeout: %s' % e)

        if options['delete_index'] and options['confirm']:
            try:
                delete_index()
            except requests.exceptions.ConnectionError:
                logprint('error', 'ConnectionError: check connection to MediaWiki or Elasticsearch.')
            except requests.exceptions.ReadTimeout as e:
                logprint('error', 'ReadTimeout: %s' % e)

        if options['create_index']:
            try:
                create_index()
            except requests.exceptions.ConnectionError:
                logprint('error', 'ConnectionError: check connection to MediaWiki or Elasticsearch.')
            except requests.exceptions.ReadTimeout as e:
                logprint('error', 'ReadTimeout: %s' % e)

        if options['topics']:
            try:
                topics(report=options['report'], dryrun=options['dryrun'])
            except requests.exceptions.ConnectionError:
                logprint('error', 'ConnectionError: check connection to MediaWiki or Elasticsearch.')
            except requests.exceptions.ReadTimeout as e:
                logprint('error', 'ReadTimeout: %s' % e)

        if options['authors']:
            try:
                authors(report=options['report'], dryrun=options['dryrun'])
            except requests.exceptions.ConnectionError:
                logprint('error', 'ConnectionError: check connection to MediaWiki or Elasticsearch.')
            except requests.exceptions.ReadTimeout as e:
                logprint('error', 'ReadTimeout: %s' % e)

        if options['articles']:
            try:
                articles(report=options['report'], dryrun=options['dryrun'])
            except requests.exceptions.ConnectionError:
                logprint('error', 'ConnectionError: check connection to MediaWiki or Elasticsearch.')
            except requests.exceptions.ReadTimeout as e:
                logprint('error', 'ReadTimeout: %s' % e)
