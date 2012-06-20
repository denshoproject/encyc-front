from datetime import datetime
import json

import requests

from django.conf import settings


def published_sources():
    """Returns list of published Sources.
    """
    sources = []
    TS_FORMAT = '%Y-%m-%d %H:%M:%S'
    url = '%s/primarysource/sitemap/' % settings.TANSU_API
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code == 200:
        response = json.loads(r.text)
        for s in response['objects']:
            s['modified'] = datetime.strptime(s['modified'], TS_FORMAT)
            sources.append(s)
    return sources
