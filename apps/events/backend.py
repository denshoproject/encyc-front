from datetime import datetime
import json

import requests

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.template import loader, Context

from wikiprox import make_cache_key


def events():
    """Returns list of events.
    """
    cache_key = make_cache_key('wikiprox:events:events')
    objects = []
    cached = cache.get(cache_key)
    if cached:
        objects = json.loads(cached)
    else:
        url = '%s/events/' % settings.TANSU_API
        r = requests.get(url, headers={'content-type':'application/json'})
        if r.status_code == 200:
            response = json.loads(r.text)
            for obj in response['objects']:
                objects.append(obj)
        cache.set(cache_key, json.dumps(objects), settings.CACHE_TIMEOUT)
    return objects
