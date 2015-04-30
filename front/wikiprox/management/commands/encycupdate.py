"""Commands for updating Elasticsearch using data from MediaWiki.

Add this to `/etc/crontab`:

    SHELL=/bin/bash
    MIN *     * * *   encyc     cd /usr/local/src/encyc-front/front && /usr/local/src/env/front/bin/python manage.py encycupdate

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
from wikiprox.models.legacy import Proxy
from wikiprox.models import Elasticsearch
from wikiprox.models import Author, Page, Source


def logprint(level, msg):
    print('%s %s' % (datetime.now(), msg))
    if   level == 'debug': logging.debug(msg)
    elif level == 'info': logging.info(msg)
    elif level == 'error': logging.error(msg)

def reset():
    logprint('debug', 'hosts: %s' % settings.DOCSTORE_HOSTS)
    connections.create_connection(hosts=settings.DOCSTORE_HOSTS)
    logprint('debug', 'index: %s' % settings.DOCSTORE_INDEX)
    index = Index(settings.DOCSTORE_INDEX)

    logprint('debug', 'deleting old index')
    index.delete()
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

def authors():
    logprint('debug', 'hosts: %s' % settings.DOCSTORE_HOSTS)
    connections.create_connection(hosts=settings.DOCSTORE_HOSTS)
    logprint('debug', 'index: %s' % settings.DOCSTORE_INDEX)
    index = Index(settings.DOCSTORE_INDEX)

    logprint('debug', 'getting mw_authors...')
    mw_authors = Proxy().authors(cached_ok=False)
    logprint('debug', '%s' % len(mw_authors))
    logprint('debug', 'getting es_authors...')
    es_authors = Author.authors()
    logprint('debug', '%s' % len(es_authors))
    logprint('debug', 'determining new,delete...')
    authors_new,authors_delete = Elasticsearch().authors_to_update(mw_authors, es_authors)
    logprint('debug', 'authors_new    %s' % len(authors_new))
    logprint('debug', 'authors_delete %s' % len(authors_delete))
    
    logprint('debug', 'deleting...')
    for n,title in enumerate(authors_delete):
        logprint('debug', '------------------------------------------------------------------------')
        logprint('debug', '%s/%s %s' % (n, len(authors_delete), title))
        author = Author.get(url_title=title)
        author.delete()
     
    logprint('debug', 'adding...')
    for n,title in enumerate(authors_new):
        logprint('debug', '------------------------------------------------------------------------')
        logprint('debug', '%s/%s %s' % (n, len(authors_new), title))
        logprint('debug', 'getting from mediawiki')
        mwauthor = Proxy().page(title)
        logprint('debug', 'creating author')
        author = Author.from_mw(mwauthor)
        logprint('debug', 'saving')
        author.save()
        try:
            a = Author.get(title)
        except NotFoundError:
            logprint('error', 'ERROR: Author(%s) NOT SAVED!' % title)
        logprint('debug', 'ok')

def articles():
    logprint('debug', 'hosts: %s' % settings.DOCSTORE_HOSTS)
    connections.create_connection(hosts=settings.DOCSTORE_HOSTS)
    logprint('debug', 'index: %s' % settings.DOCSTORE_INDEX)
    index = Index(settings.DOCSTORE_INDEX)
    
    # authors need to be refreshed
    logprint('debug', 'getting mw_authors,articles...')
    mw_authors = Proxy().authors(cached_ok=False)
    mw_articles = Proxy().articles_lastmod()
    logprint('debug', '%s mediawiki articles' % len(mw_articles))
    logprint('debug', 'getting es_authors,articles...')
    es_authors = Author.authors()
    es_articles = Page.pages()
    logprint('debug', '%s elasticsearch articles' % len(es_articles))
    logprint('debug', 'determining new,delete...')
    articles_update,articles_delete = Elasticsearch().articles_to_update(
        mw_authors, mw_articles, es_authors, es_articles)
    logprint('debug', 'articles_update: %s' % len(articles_update))
    logprint('debug', 'articles_delete: %s' % len(articles_delete))
     
    logprint('debug', 'adding articles...')
    posted = 0
    could_not_post = []
    for n,title in enumerate(articles_update):
        logprint('debug', '------------------------------------------------------------------------')
        logprint('debug', '%s/%s %s' % (n+1, len(articles_update), title))
        logprint('debug', 'getting from mediawiki')
        mwpage = Proxy().page(title)
        if (mwpage.published or settings.WIKIPROX_SHOW_UNPUBLISHED):
            page_sources = [source['encyclopedia_id'] for source in mwpage.sources]
            for mwsource in mwpage.sources:
                logprint('debug', '- source %s' % mwsource['encyclopedia_id'])
                source = Source.from_mw(mwsource)
                source.save()
            logprint('debug', 'creating page')
            page = Page.from_mw(mwpage)
            logprint('debug', 'saving')
            page.save()
            try:
                p = Page.get(title)
            except NotFoundError:
                logprint('error', 'ERROR: Page(%s) NOT SAVED!' % title)
            logprint('debug', 'ok')
        else:
            could_not_post.append(page)
            logprint('debug', 'not publishable')
    if could_not_post:
        logprint('debug', '========================================================================')
        logprint('debug', 'Could not post these: %s' % could_not_post)
        logging.debug('Could not post these: %s' % could_not_post)


class Command(BaseCommand):
    help = 'Updates authors and articles.'
    
    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_const', const=1, help='Create new index.')
        parser.add_argument('--authors', action='store_const', const=1, help='Index authors.')
        parser.add_argument('--articles', action='store_const', const=1, help='Index articles.')
    
    def handle(self, *args, **options):
        if not (options['reset'] or options['authors'] or options['articles']):
            print('Choose an action. Try "python manage.py encycupdate --help".')
            sys.exit(1)
        try:
            if options['reset']:
                reset()
            elif options['authors']:
                authors()
            elif options['articles']:
                articles()
        except requests.exceptions.ConnectionError:
            logprint('error', 'ConnectionError: check connection to MediaWiki or Elasticsearch.')
        except requests.exceptions.ReadTimeout as e:
            logprint('error', 'ReadTimeout: %s' % e)
