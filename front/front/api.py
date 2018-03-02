from django.core.urlresolvers import reverse

from rest_framework.decorators import api_view
from rest_framework.response import Response


def http_host(request):
    return 'https://%s' % request.META['HTTP_HOST']

def makeurl(request, uri):
    return '%s%s' % (http_host(request), uri)


@api_view(['GET'])
def index(request, format=None):
    """DOCUMENTATION GOES HERE.
    """
    data = {
        'articles': makeurl(request, reverse('wikiprox-api-articles')),
        'authors': makeurl(request, reverse('wikiprox-api-authors')),
        'categories': makeurl(request, reverse('wikiprox-api-categories')),
        'events': makeurl(request, reverse('events-api-events')),
        'locations': makeurl(request, reverse('locations-api-locations')),
    }
    return Response(data)
