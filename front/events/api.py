import requests

from django.conf import settings
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from events import backend as ev


def http_host(request):
    return 'http://%s' % request.META['HTTP_HOST']

def makeurl(request, uri):
    return '%s%s' % (http_host(request), uri)


@api_view(['GET'])
def events(request, format=None):
    """DOCUMENTATION GOES HERE.
    """
    try:
        data = ev.events()
    except requests.exceptions.Timeout:
        return Response(status=status.HTTP_408_REQUEST_TIMEOUT)
    return Response(data)
