from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)
from urllib.parse import urlparse

from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Index
from elasticsearch_dsl import DocType, String, Date, Nested, Boolean, analysis
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
import requests

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

MAX_SIZE = 10000

# set default hosts and index
connections.create_connection(hosts=settings.DOCSTORE_HOSTS)
index = Index(settings.DOCSTORE_INDEX)


def hitvalue(hit, field):
    """
    For some reason, Search hit objects wrap values in lists.
    returns the value inside the list.
    """
    if hit.get(field) and isinstance(hit[field], list):
        value = hit[field][0]
    else:
        value = hit.get(field, '')
    return value


class Event(DocType):
    """
    IMPORTANT: uses Elasticsearch-DSL, not the Django ORM.
    """
    id = String(index='not_analyzed')  # Elasticsearch id
    published = Boolean()
    title = String()
    description = String()
    start_date = Date()
    end_date = Date()
    article_title = String(index='not_analyzed')
    resource_uri = String(index='not_analyzed')
    
    class Meta:
        index = settings.DOCSTORE_INDEX
        doc_type = 'events'
    
    def __repr__(self):
        cutoff = 30
        ymd = '-'.join([
            str(self.start_date.year),
            str(self.start_date.month),
            str(self.start_date.day),
        ])
        if self.title:
            return "<Event '%s: %s'>" % (ymd, self.title)
        elif len(self.description) > cutoff:
            return "<Event '%s: %s...'>" % (ymd, self.description[:cutoff])
        else:
            return "<Event '%s: %s'>" % (ymd, self.description)
    
    def __str__(self):
        return self.__repr__()
    
    #def absolute_url(self):
    #    return reverse('url title', args=([self.id,]))

    @staticmethod
    def events():
        """Returns list of Event objects.
        
        @returns: list
        """
        s = Search(doc_type='events')[0:MAX_SIZE]
        s = s.sort('start_date')
        s = s.fields([
            'id',
            'published',
            'title',
            'description',
            'start_date',
            'end_date',
            'article_title',
            'resource_uri',
        ])
        response = s.execute()
        data = [
            Event(
                id = hit.meta.id,
                published = hitvalue(hit, 'published'),
                title = hitvalue(hit, 'title'),
                description = hitvalue(hit, 'description'),
                start_date = hitvalue(hit, 'start_date'),
                end_date = hitvalue(hit, 'end_date'),
                article_title = hitvalue(hit, 'article_title'),
                resource_uri = hitvalue(hit, 'resource_uri'),
            )
            for hit in response
        ]
        return data
    
    @staticmethod
    def from_psms():
        """Gets data from encyc-psms and returns list of Events.
        """
        url = '%s/events/' % settings.SOURCES_API
        r = requests.get(
            url, params={'limit':1000},
            headers={'content-type':'application/json'},
            timeout=10)
        objects = []
        if r and r.status_code == 200:
            response = json.loads(r.text)
            for obj in response['objects']:
                objects.append(obj)
        # convert all the dates
        for obj in objects:
            if obj.get('start_date',None):
                obj['start_date'] = datetime.strptime(obj['start_date'], '%Y-%m-%d')
            if obj.get('end_date',None):
                obj['end_date'] = datetime.strptime(obj['end_date'], '%Y-%m-%d')
        # keep just the encyclopedia article title
        for obj in objects:
            obj['article_title'] = ''
            if obj.get('url'):
                path = urlparse.urlparse(obj['url']).path
                if path[0] == '/':
                    obj['article_title'] = path[1:]
                else:
                    obj['article_title'] = path
        # make Events
        events = [
            Event(
                meta = {'id': obj['id']},
                published = int(obj['published']),
                title = obj['title'],
                description = obj['description'],
                start_date = obj['start_date'],
                end_date = obj['end_date'],
                article_title = obj['article_title'],
                resource_uri = obj['resource_uri'],
            )
            for obj in objects
        ]
        return events
