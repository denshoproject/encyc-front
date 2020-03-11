from datetime import datetime

from django.conf import settings
from django.contrib.sitemaps import Sitemap

from wikiprox import models


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
        for p in models.Page.pages():
            item = Item()
            item.title = p.title
            item.location = p.absolute_url()
            item.timestamp = p.modified
            items.append(item)
        return items
    
    def lastmod(self, obj):
        return obj.timestamp

class SourceSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    
    def items(self):
        items = []
        for s in models.Source.sources():
            item = Item()
            item.title = s.encyclopedia_id
            item.location = s.absolute_url()
            item.timestamp = s.modified
            items.append(item)
        return items
    
    def lastmod(self, obj):
        return obj.timestamp
