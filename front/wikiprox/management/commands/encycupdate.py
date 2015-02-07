"""
Add this to `/etc/crontab`:

    SHELL=/bin/bash
    MIN *     * * *   encyc     cd /usr/local/src/encyc-front/front && /usr/local/src/env/front/bin/python manage.py encycupdate

"""

import logging
logger = logging.getLogger(__name__)
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from wikiprox import models


class Command(BaseCommand):
    help = 'Updates authors and articles.'
    
    def handle(self, *args, **options):
        # authors
        mw_authors = models.Proxy().authors(cached_ok=False)
        es_authors = models.Elasticsearch().authors()
        author_results = models.Elasticsearch().authors_to_update(
            mw_authors, es_authors)
        models.Elasticsearch().delete_authors(titles=author_results['delete'])
        models.Elasticsearch().index_authors(titles=author_results['new'])
        
        # articles
        # authors need to be refreshed
        mw_authors = models.Proxy().authors(cached_ok=False)
        mw_articles = models.Proxy().articles_lastmod()
        es_authors = models.Elasticsearch().authors()
        es_articles = models.Elasticsearch().articles()
        article_results = models.Elasticsearch().articles_to_update(
            mw_authors, mw_articles, es_authors, es_articles)
        models.Elasticsearch().delete_articles(titles=article_results['delete'])
        models.Elasticsearch().index_articles(titles=article_results['update'])
        
