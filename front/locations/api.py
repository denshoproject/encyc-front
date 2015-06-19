import requests

from django.conf import settings
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from locations import backend as loc


def http_host(request):
    return 'http://%s' % request.META['HTTP_HOST']

def makeurl(request, uri):
    return '%s%s' % (http_host(request), uri)


@api_view(['GET'])
def locations(request, format=None):
    """DOCUMENTATION GOES HERE.
    """
    try:
        locations = loc.locations()
    except requests.exceptions.Timeout:
        return Response(status=status.HTTP_408_REQUEST_TIMEOUT)
    data = [
        {
            'id': c[0],
            'title': c[1],
            'url': makeurl(request, reverse('locations-api-category', args=([c[0]]))),
        }
        for c in loc.categories(locations)
    ]
    return Response(data)

@api_view(['GET'])
def category(request, category, format=None):
    """DOCUMENTATION GOES HERE.
    """
    try:
        locations = loc.locations()
    except requests.exceptions.Timeout:
        return Response(status=status.HTTP_408_REQUEST_TIMEOUT)
    data = loc.filter_by_category(locations, category)
    for category in data:
        if category['location_uri']:
            url = makeurl(request, reverse('wikiprox-api-page', args=([category['location_uri']])))
            category['location_url'] = url
    return Response(data)
