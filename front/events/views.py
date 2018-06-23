import requests

from django.conf import settings
from django.shortcuts import render

from events import backend as ev


def events(request, template_name='events/events.html'):
    try:
        events = ev.events()
        timeout = False
    except requests.exceptions.Timeout:
        events = []
        timeout = True
    return render(request, template_name, {
        'events': events,
        'timeout': timeout,
    })
