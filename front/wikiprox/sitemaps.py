from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sitemaps import Sitemap

from wikiprox import models


class Item(object):
    location = ''
    timestamp = None
    
    def unicode(self):
        self.title
    
    def get_absolute_url(self):
        return urlparse(self.location).path
    
class MediaWikiSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5
    protocol = 'https'
    
    def items(self):
        items = []
        for p in models.Page.pages():
            item = Item()
            item.title = p.title
            item.location = urlparse(p.absolute_url()).path
            if item.location[-1] != '/':
                item.location = f'{item.location}/'
            item.timestamp = p.modified
            items.append(item)
        return items
    
    def lastmod(self, obj):
        if isinstance(obj.timestamp, datetime):
            return obj.timestamp

class SourceSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5
    protocol = 'https'
    
    def items(self):
        items = []
        for s in models.Source.sources():
            item = Item()
            item.title = s.encyclopedia_id
            item.location = urlparse(s.absolute_url()).path
            item.timestamp = s.modified
            items.append(item)
        return items
    
    def lastmod(self, obj):
        if isinstance(obj.timestamp, datetime):
            return obj.timestamp
