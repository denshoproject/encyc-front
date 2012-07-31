from datetime import datetime
import json

import requests

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.template import loader, Context

from wikiprox import make_cache_key


def locations():
    """Returns list of locations.
    """
    locations = []
    cache_key = make_cache_key('wikiprox:locations:locations')
    cached = cache.get(cache_key)
    if cached:
        locations = json.loads(cached)
    else:
        url = '%s/locations/' % settings.TANSU_API
        r = requests.get(url, headers={'content-type':'application/json'})
        if r.status_code == 200:
            response = json.loads(r.text)
            for location in response['objects']:
                locations.append(location)
        cache.set(cache_key, json.dumps(locations), settings.CACHE_TIMEOUT)
    return locations
