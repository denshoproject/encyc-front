from datetime import datetime
import json

from bs4 import BeautifulSoup
import requests

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import loader, Context


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

def format_primary_source(source):
    # context
    common = {'media_format': source['media_format'],
              'MEDIA_URL': settings.MEDIA_URL,
              'SOURCE_MEDIA_URL': settings.TANSU_MEDIA_URL,
              'href': reverse('wikiprox-source', args=[source['encyclopedia_id']]),
              'caption': source['caption'],
              'courtesy': source['courtesy'],}
    specific = {}
    # video
    if source['media_format'] == 'video':
        template = 'wikiprox/video.html'
        if source.get('thumbnail_sm',None):
            thumb_sm = source['thumbnail_sm']
            thumb_lg = source['thumbnail_lg']
        elif source.get('display',None):
            thumb_sm = source['display']
            thumb_lg = source['display']
        else:
            thumb_sm = 'img/icon-video.png'
            thumb_lg = 'img/icon-video.png'
        xy = [640,480]
        if source.get('aspect_ratio',None) and (source['aspect_ratio'] == 'hd'):
            xy = [640,360]
        # remove rtmp_streamer from streaming_url
        if source.get('streaming_url',None) and ('rtmp' in source['streaming_url']):
            streaming_url = source['streaming_url'].replace(settings.RTMP_STREAMER, '')
            rtmp_streamer = settings.RTMP_STREAMER
        else:
            streaming_url = source['streaming_url']
            rtmp_streamer = ''
        # add 20px to vertical for JWplayer
        xy[1] = xy[1] + 20
        specific = {
            'thumb_sm': thumb_sm,
            'thumb_lg': thumb_lg,
            'rtmp_streamer': rtmp_streamer,
            'streaming_url': streaming_url,
            'xy': xy,
            }
    # document
    elif source['media_format'] == 'document':
        template = 'wikiprox/document.html'
        if source.get('thumbnail_sm',None):
            thumb_sm = source['thumbnail_sm']
            thumb_lg = source['thumbnail_lg']
        elif source.get('display',None):
            thumb_sm = source['thumbnail_sm']
            thumb_lg = source['thumbnail_lg']
        elif source.get('original',None):
            thumb_sm = source['original']
            thumb_lg = source['original']
        else:
            thumb_sm = 'img/icon-document.png'
            thumb_lg = 'img/icon-document.png'
        specific = {
            'thumb_sm': thumb_sm,
            'thumb_lg': thumb_lg,
            }
    # image
    elif source['media_format'] == 'image':
        template = 'wikiprox/image.html'
        # img src
        if source.get('thumbnail_sm',None):
            thumb_sm = source['thumbnail_sm']
            thumb_lg = source['thumbnail_lg']
        elif source.get('display',None):
            thumb_sm = source['display']
            thumb_lg = source['display']
        elif source.get('original',None):
            thumb_sm = source['original']
            thumb_lg = source['original']
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
