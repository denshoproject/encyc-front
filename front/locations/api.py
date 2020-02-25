import requests

from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from locations import backend as loc


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
            'url': reverse('locations-api-category', args=([c[0]])),
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
            url = reverse('wikiprox-api-page', args=([category['location_uri']]))
            category['location_url'] = url
    return Response(data)
