import requests

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

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
    return render(request, template_name, {
        'categories': categories,
        'locations': locations,
        'timeout': timeout,
    })

#def locations_kml(request, category=None):
#    try:
#        locations = loc.locations()
#    except requests.exceptions.Timeout:
#        return HttpResponse(status=408)
#    locations = loc.filter_by_category(locations, category)
#    kml = loc.kml(locations)
#    return HttpResponse(kml, content_type="text/xml")
