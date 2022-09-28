"""front.ddr -- Links to the DDR REST API
"""
import json
import os

import requests

from django.conf import settings
from django.core.cache import cache

from wikiprox import make_cache_key


def _term_documents(term_id, size):
    """Get objects for specified term from DDR REST API.
    
    @param term_id: int
    @param size: int Maximum number of results to return.
    @returns: list of dicts
    """
    cache_key = make_cache_key('wikiprox:ddr:termdocs:%s:%s' % (term_id,size))
    cached = cache.get(cache_key)
    if cached:
        objects = json.loads(cached)
    else:
        url = '{api}/facet/topics/{term_id}/objects/?limit={limit}&{local}=1'.format(
            api=settings.DDR_API,
            term_id=term_id,
            limit=size,
            local=settings.DDR_MEDIA_URL_LOCAL_MARKER
        )
        r = requests.get(
            url,
            headers={'content-type':'application/json'},
            timeout=3)
        if (r.status_code not in [200]):
            raise requests.exceptions.ConnectionError(
                'Error %s' % (r.status_code))
        objects = []
        if ('json' in r.headers['content-type']):
            data = json.loads(r.text)
            if isinstance(data, dict) and data.get('objects'):
                objects = data['objects']
            elif isinstance(data, list):
                objects = data
        # add img_url_local
        for o in objects:
            if o.get('links',{}).get('html'):
                o['absolute_url'] = o['links']['html']
            if o.get('links',{}).get('thumb'):
                o['img_url'] = o['links']['img']
            if o.get('links',{}).get('thumb'):
                o['img_url_local'] = o['links']['thumb']
        cache.set(cache_key, json.dumps(objects), settings.CACHE_TIMEOUT)
    return objects

def _balance(results, size):
    """cycle through term IDs taking one at a time until we have enough
    
    @param results: dict of search results keyed to term IDs.
    @param size: int Maximum number of results to return.
    """
    if not results:
        return []
    limit = min([size, len(results.keys())])
    round1 = []
    while(len(round1) < limit):
        for tid in results.keys():
            doc = None
            if results[tid]:
                doc = results[tid].pop()
            round1.append(doc)
    # remove empties
    round2 = [doc for doc in round1 if doc]
    return round2

def distribute_dict(terms_objects, limit):
    """Given list of term:object dicts, limit to N objects.
    
    Ensures no more than {limit} total objects, as evenly distributed
    among the terms as possible.
    
    terms_objects = [
        {
            'id':123, 'title':'Term 0',
            'objects': [
                'thing 1',
                'thing 2',
            ]
        },
        {
            'id':124, 'title':'Term 1',
            'objects': [
                'object0',
                'object1',
                'object2',
            ]
        },
        ...
    ]
    
    @param terms_objects: list of dicts
    @param limit: int
    @returns: dict
    """
    if not terms_objects:
        return {}
    termid_objs = {}
    hits = 0   # so we don't add too many
    misses = 0 # prevent infinite loop
    while (hits < limit) and (misses < limit):
        for term in terms_objects:
            term_id = term['id']
            if not termid_objs.get(term_id):
                termid_objs[term_id] = []
            if term['objects'] and (hits < limit):
                o = term['objects'].pop(0)
                termid_objs[term_id].append(o)
                hits = hits + 1
            else:
                misses = misses + 1
    for term in terms_objects:
        term['objects'] = termid_objs.pop(term['id'])
    return terms_objects

def distribute_list(terms_objects, limit):
    """Given list of term:object dicts, make list of {limit} objects.
    
    @param terms_objects: list of dicts
    @param limit: int
    @returns: list
    """
    if not terms_objects:
        return []
    objects = []
    hits = 0   # so we don't add too many
    misses = 0 # prevent infinite loop
    while (hits < limit) and (misses < limit):
        for term in terms_objects:
            term_id = term['id']
            if term['objects'] and (hits < limit):
                objects.append(term['objects'].pop(0))
                hits = hits + 1
            else:
                misses = misses + 1
    return objects

def related_by_topic(terms, size):
    """Add related documents from DDR to terms
    
    @param terms: list of FacetTerms.
    @param size: int Number of results per term.
    """
    for term in terms:
        term['objects'] = _term_documents(term['term_id'], size)
    return terms
