from datetime import datetime

from django.conf import settings
from django.contrib.sitemaps import Sitemap

from wikiprox.encyclopedia import published_pages
from wikiprox.sources import published_sources


class Item(object):
    location = ''
    timestamp = None
    def unicode(self):
        self.title
    def get_absolute_url(self):
        return self.location


class MediaWikiSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        items = []
        for p in published_pages():
            item = Item()
            item.title = p['title']
            item.location = '/%s/' % p['title']
            item.timestamp = datetime.strptime(p['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
            items.append(item)
        return items

    def lastmod(self, obj):
        return obj.timestamp


class SourceSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        items = []
        for s in published_sources():
            item = Item()
            item.title = s['encyclopedia_id']
            item.location = '/sources/%s/' % s['encyclopedia_id']
            item.timestamp = datetime.strptime(s['modified'], '%Y-%m-%d %H:%M:%S')
            items.append(item)
        return items
    
    def lastmod(self, obj):
        return obj.timestamp
