from datetime import datetime
import json

from bs4 import BeautifulSoup
import requests

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.template import loader, Context

from wikiprox import make_cache_key

TS_FORMAT = '%Y-%m-%d %H:%M:%S'


def source(encyclopedia_id):
    source = None
    url = '%s/primarysource/?encyclopedia_id=%s' % (settings.TANSU_API, encyclopedia_id)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code == 200:
        response = json.loads(r.text)
        if response and (response['meta']['total_count'] == 1):
            source = response['objects'][0]
    return source

def published_sources():
    """Returns list of published Sources.
    """
    sources = []
    cache_key = make_cache_key('wikiprox:sources:published_sources')
    cached = cache.get(cache_key)
    if cached:
        sources = json.loads(cached)
        for source in sources:
            source['modified'] = datetime.strptime(source['modified'], TS_FORMAT)
    else:
        url = '%s/primarysource/sitemap/' % settings.TANSU_API
        r = requests.get(url, headers={'content-type':'application/json'})
        if r.status_code == 200:
            response = json.loads(r.text)
            sources = [source for source in response['objects']]
        cache.set(cache_key, json.dumps(sources), settings.CACHE_TIMEOUT)
    return sources

def format_primary_source(source, lightbox=False):
    template = 'wikiprox/generic.html'
    # context
    common = {'encyclopedia_id': source.encyclopedia_id,
              'media_format': source.media_format,
              'MEDIA_URL': settings.MEDIA_URL,
              'STATIC_URL': settings.STATIC_URL,
              'SOURCE_MEDIA_URL': settings.TANSU_MEDIA_URL,
              'href': source.absolute_url(),
              'caption': source.caption,
              'courtesy': source.courtesy,
              'lightbox': lightbox,}
    specific = {}
    # video
    if source.media_format == 'video':
        template = 'wikiprox/video.html'
        if source.thumbnail_sm:
            thumb_sm = source.thumbnail_sm
            thumb_lg = source.thumbnail_lg
        elif source.display:
            thumb_sm = source.display
            thumb_lg = source.display
        else:
            thumb_sm = 'img/icon-video.png'
            thumb_lg = 'img/icon-video.png'
        if source.original_url:
            original_url = source.original_url
        else:
            original_url = ''
        xy = [640,480]
        if source.aspect_ratio and (source.aspect_ratio == 'hd'):
            xy = [640,360]
        # remove rtmp_streamer from streaming_url
        if source.streaming_url and ('rtmp' in source.streaming_url):
            streaming_url = source.streaming_url.replace(settings.RTMP_STREAMER, '')
            rtmp_streamer = settings.RTMP_STREAMER
        else:
            streaming_url = source.streaming_url
            rtmp_streamer = ''
        # add 20px to vertical for JWplayer
        xy[1] = xy[1] + 20
        # mediaspace <div>
        xyms = [xy[0]+10, xy[1]+10]
        specific = {
            'thumb_sm': thumb_sm,
            'thumb_lg': thumb_lg,
            'original': original_url,
            'rtmp_streamer': rtmp_streamer,
            'streaming_url': streaming_url,
            'xy': xy,
            'xyms': xyms,
            }
    # document
    elif source.media_format == 'document':
        template = 'wikiprox/document.html'
        if source.thumbnail_sm:
            thumb_sm = source.thumbnail_sm
            thumb_lg = source.thumbnail_lg
        elif source.display:
            thumb_sm = source.thumbnail_sm
            thumb_lg = source.thumbnail_lg
        elif source.original_url:
            thumb_sm = source.original_url
            thumb_lg = source.original_url
        else:
            thumb_sm = 'img/icon-document.png'
            thumb_lg = 'img/icon-document.png'
        specific = {
            'thumb_sm': thumb_sm,
            'thumb_lg': thumb_lg,
            }
    # image
    elif source.media_format == 'image':
        template = 'wikiprox/image.html'
        # img src
        if source.thumbnail_sm:
            thumb_sm = source.thumbnail_sm
            thumb_lg = source.thumbnail_lg
        elif source.display:
            thumb_sm = source.display
            thumb_lg = source.display
        elif source.original_url:
            thumb_sm = source.original_url
            thumb_lg = source.original_url
        else:
            thumb_sm = 'img/icon-image.png'
            thumb_lg = 'img/icon-image.png'
        specific = {
            'thumb_sm': thumb_sm,
            'thumb_lg': thumb_lg,
            }
    context = dict(common.items() + specific.items())
    # render
    t = loader.get_template(template)
    c = Context(context)
    return t.render(c)

def replace_source_urls(sources, request):
    """rewrite sources URLs to point to stage domain:port
    
    When viewing the stage site through SonicWall, Android Chrome browser
    won't display media from the outside (e.g. encyclopedia.densho.org).
    """
    fields = ['display','original','streaming_url','thumbnail_lg','thumbnail_sm',]
    old_domain = None
    if hasattr(settings,'STAGE_MEDIA_DOMAIN') and settings.STAGE_MEDIA_DOMAIN:
        old_domain = settings.STAGE_MEDIA_DOMAIN
    new_domain = request.META['HTTP_HOST']
    if new_domain.find(':') > -1:
        new_domain = new_domain.split(':')[0]
    if old_domain and new_domain:
        for source in sources:
            for f in fields:
                if source.get(f,None):
                    source[f] = source[f].replace(old_domain, new_domain)
    return sources
