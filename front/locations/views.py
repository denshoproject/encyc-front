import requests

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_http_methods

from locations import backend as loc


def locations(request, category=None, template_name='locations/locations.html'):
    try:
        locations = loc.locations()
        timeout = False
    except requests.exceptions.Timeout:
        locations = []
        timeout = True
    locations = loc.filter_by_category(locations, category)
    categories = loc.categories(locations)
    return render_to_response(
        template_name,
        {'categories': categories,
         'locations': locations,
         'timeout': timeout,},
        context_instance=RequestContext(request)
    )

def locations_kml(request, category=None):
    try:
        locations = loc.locations()
    except requests.exceptions.Timeout:
        return HttpResponse(status=408)
    locations = loc.filter_by_category(locations, category)
    kml = loc.kml(locations)
    return HttpResponse(kml, content_type="text/xml")
