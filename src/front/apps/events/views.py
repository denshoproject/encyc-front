from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_http_methods

from events import backend as ev


def events(request, template_name='events/events.html'):
    events = ev.events()
    return render_to_response(
        template_name,
        {'events': events,},
        context_instance=RequestContext(request)
    )
