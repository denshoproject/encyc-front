from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def index(request, format=None):
    """DOCUMENTATION GOES HERE.
    """
    data = {
        'articles': reverse('wikiprox-api-articles', request=request),
        'authors': reverse('wikiprox-api-authors', request=request),
        'categories': reverse('wikiprox-api-categories', request=request),
        'events': reverse('events-api-events', request=request),
    }
    return Response(data)
