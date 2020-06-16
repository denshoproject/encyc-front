from datetime import datetime
import json

import requests

from django.conf import settings
from django.core.cache import cache
from django.template import loader
from django.urls import reverse

from wikiprox import make_cache_key


def source(encyclopedia_id):
    source = None
    url = '%s/primarysource/?encyclopedia_id=%s' % (settings.SOURCES_API, encyclopedia_id)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code == 200:
        response = json.loads(r.text)
        if response and (response['meta']['total_count'] == 1):
            source = response['objects'][0]
    return source

def format_primary_source(source, lightbox=False):
    template = 'wikiprox/primarysource-%s.html' % source.media_format
    context = {
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
        'SOURCES_MEDIA_URL': settings.SOURCES_MEDIA_URL,
        'RTMP_STREAMER': settings.RTMP_STREAMER,
        'lightbox': lightbox,
        'source': source,
    }
    if source.media_format == 'video':
        xy = [640,480]
        if source.aspect_ratio and (source.aspect_ratio == 'hd'):
            xy = [640,360]
        # add 20px to vertical for JWplayer
        xy[1] = xy[1] + 20
        # mediaspace <div>
        xyms = [xy[0]+10, xy[1]+10]
        # add to context
        context['xy'] = xy
        context['xyms'] = xyms
    # render
    return loader.get_template(template).render(context)
