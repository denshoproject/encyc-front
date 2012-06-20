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
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        items = []
        for p in published_pages():
            item = Item()
            item.title = p['title']
            item.location = p['location']
            item.timestamp = p['timestamp']
            items.append(item)
        return items

    def lastmod(self, obj):
        return obj.timestamp


class SourceSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        items = []
        for s in published_sources():
            item = Item()
            item.title = s['encyclopedia_id']
            item.location = '/sources/%s/' % s['encyclopedia_id']
            item.timestamp = s['modified']
            items.append(item)
        return items
    
    def lastmod(self, obj):
        return obj.timestamp
