from datetime import datetime
import json

import requests

from django.conf import settings
from django.contrib.sitemaps import Sitemap


class Page(object):
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
        pages = []
        #
        LIMIT = 5000
        TS_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
        url = '%s?action=query&generator=allpages&prop=revisions&rvprop=timestamp&gaplimit=%s&format=json' % (settings.WIKIPROX_MEDIAWIKI_API, LIMIT)
        r = requests.get(url)
        if r.status_code == 200:
            response = json.loads(r.text)
            if response and response['query'] and response['query']['pages']:
                ids = []
                for id  in response['query']['pages'].keys():
                    if id not in ids:
                        ids.append(id)
                for id in ids:
                    p = response['query']['pages'][id]
                    page = Page()
                    page.title = p['title']
                    page.location = '/wiki/%s/' % p['title']
                    page.timestamp = datetime.strptime(p['revisions'][0]['timestamp'], TS_FORMAT)
                    pages.append(page)
        return pages

    def lastmod(self, obj):
        return obj.timestamp
