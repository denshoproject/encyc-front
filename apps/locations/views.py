from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_http_methods

from locations import backend as loc


def locations(request, category=None, template_name='locations/locations.html'):
    locations = loc.filter_by_category(loc.locations(), category)
    categories = loc.categories(locations)
    return render_to_response(
        template_name,
        {'categories': categories,
         'locations': locations,},
        context_instance=RequestContext(request)
    )

def locations_kml(request, category=None):
    locations = loc.filter_by_category(loc.locations(), category)
    kml = loc.kml(locations)
    return HttpResponse(kml, content_type="text/xml")
