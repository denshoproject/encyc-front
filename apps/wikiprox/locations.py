from datetime import datetime
import json

from lxml import etree
from pykml.factory import KML_ElementMaker as KML
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
        r = requests.get(url, params={'limit':'1000'},
                         headers={'content-type':'application/json'})
        if r.status_code == 200:
            response = json.loads(r.text)
            for location in response['objects']:
                locations.append(location)
        cache.set(cache_key, json.dumps(locations), settings.CACHE_TIMEOUT)
    return locations

def layers(locations):
    layers = []
    for l in locations:
        if l.get('category',None) and l['category']:
            layer = ( l['category'], l['category_name'] )
            if layer not in layers:
                layers.append(layer)
    return layers

def kml(locations):
    document = KML.kml(KML.Document(KML.name("Layer example")))
    # bullets
    for layer in layers(locations):
        layer_code = layer[0]
        style = KML.Style(
            KML.IconStyle(
                KML.scale(1.0),
                KML.Icon(
                    KML.href('%slocations/%s.png' % (settings.MEDIA_URL, layer_code)),
                ),
                id='icon-%s' % layer_code
            ),
            id=layer_code
        )
        document.append(style)
    # locations
    folder = KML.Folder()
    for location in locations:
        placemark = KML.Placemark(
            KML.name(location['title']),
            KML.description('<![CDATA[ %s ]]>' % location['description']),
            KML.styleUrl('#%s' % location['category']),
            KML.Point(
                KML.coordinates(','.join([location['lng'],location['lat']]))
                ),
            )
        folder.append(placemark)
    document.append(folder)
    # rettsugo!
    return etree.tostring(document)
