from datetime import datetime
import json

import requests

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.template import loader

from wikiprox import make_cache_key


def locations():
    """Returns list of locations and a status message.
    """
    locations = []
    cache_key = make_cache_key('wikiprox:locations:locations')
    cached = cache.get(cache_key)
    if cached:
        locations = json.loads(cached)
    else:
        url = '%s/locations/' % settings.SOURCES_API
        r = requests.get(
            url, params={'limit':'1000'},
            headers={'content-type':'application/json'},
            timeout=3)
        if (r.status_code == 200) and ('json' in r.headers['content-type']):
            response = json.loads(r.text)
            for location in response['objects']:
                locations.append(location)
        cache.set(cache_key, json.dumps(locations), settings.CACHE_TIMEOUT)
    return locations

def categories(locations):
    """Returns list of (code,name) tuples describing facility categories
    """
    categories = []
    for l in locations:
        if l.get('category',None) and l['category']:
            category = ( l['category'], l['category_name'] )
            if category not in categories:
                categories.append(category)
    return categories

def filter_by_category(locations, category=None):
    if category:
        filtered = []
        for l in locations:
            if (l.get('category',None) and l['category'] == category):
                filtered.append(l)
        return filtered
    return locations
