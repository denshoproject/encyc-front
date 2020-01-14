import logging
logger = logging.getLogger(__name__)

from elasticsearch.exceptions import NotFoundError
import elasticsearch_dsl as dsl
import requests

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models

from locations import backend as loc



def index_locations():
    """
    @param title: str
    """
    try:
        locations = loc.locations()
        categories = loc.categories(locations)
        timeout = False
    except requests.exceptions.Timeout:
        locations = []
        categories = []
        timeout = True

    for category in categories:
        pass


            
class MapCategory(dsl.Document):
    """
    IMPORTANT: uses Elasticsearch-DSL, not the Django ORM.
    """
    id = dsl.Keyword()  # Elasticsearch id
    title = dsl.Text()
    
    class Index:
        name = 'encycmapcategory'
    
    def __repr__(self):
        return '<%s.%s "%s">' % (
            self.__module__,
            self.__class__.__name__,
            self.id
        )
    
    def __str__(self):
        return self.title
    
    def absolute_url(self):
        return reverse('locations-category', args=([self.id,]))
    
    def locations(self):
        """Returns list of Locations for this MapCategory.
        
        @returns: list
        """
        return [
            location
            for location in Location.locations()
            if location.category == self.id
        ]

    @staticmethod
    def mapcategories(num_columns=None):
        """Returns list of MapCategory objects.
        
        @returns: list
        """
        s = Search(doc_type='mapcategory')[0:MAX_SIZE]
        s = s.sort('id')
        s = s.fields([
            'id',
            'title',
        ])
        response = s.execute()
        return [
            MapCategory(
                id = hitvalue(hit, 'id'),
                title = hitvalue(hit, 'title'),
            )
            for hit in response
        ]

    @staticmethod
    def from_backend(cat):
        """Creates a MapCategory object from a locations.backend object.
        """
        mc = MapCategory(
            meta = {'id': cat.id},
        )
        return mc



class Location(dsl.Document):
    """
    IMPORTANT: uses Elasticsearch-DSL, not the Django ORM.
    """
    id = dsl.Keyword()  # Elasticsearch id
    category = dsl.Keyword()
    title = dsl.Text()
    location_name = dsl.Text()
    description = dsl.Text()
    lat = dsl.Keyword()
    lng = dsl.Keyword()
    resource_uri = dsl.Keyword()
    location_uri = dsl.Keyword()
    location_url = dsl.Keyword()
        
    class Index:
        name = 'encyclocation'
    
    def __repr__(self):
        return '<%s.%s "%s">' % (
            self.__module__,
            self.__class__.__name__,
            self.id
        )
    
    def __str__(self):
        return self.title

    @staticmethod
    def locations():
        """Returns list of Location objects.
        
        @returns: list
        """
        s = Search(doc_type='location')[0:MAX_SIZE]
        s = s.sort('id')
        s = s.fields([
            'id',
            'category',
            'title',
            'location_name',
            'description',
            'lat',
            'lng',
            'resource_uri',
            'location_uri',
            'location_url',
        ])
        response = s.execute()
        return [
            Location(
                id = hitvalue(hit, 'id'),
                category = hitvalue(hit, 'category'),
                title = hitvalue(hit, 'title'),
                location_name = hitvalue(hit, 'location_name'),
                description = hitvalue(hit, 'description'),
                lat = hitvalue(hit, 'lat'),
                lng = hitvalue(hit, 'lng'),
                resource_uri = hitvalue(hit, 'resource_uri'),
                location_uri = hitvalue(hit, 'location_uri'),
                location_url = hitvalue(hit, 'location_url'),
            )
            for hit in response
        ]
