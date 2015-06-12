"""front.ddr -- Links to the DDR REST API
"""
import json

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
        url = '%s/facet/topics/%s/objects/?limit=%s&%s=1' % (
            settings.DDR_API, term_id, size, settings.DDR_MEDIA_URL_LOCAL_MARKER
        )
        r = requests.get(
            url,
            headers={'content-type':'application/json'},
            timeout=3)
        if (r.status_code not in [200]):
            raise requests.exceptions.ConnectionError(
                'Error %s' % (r.status_code))
        if ('json' in r.headers['content-type']):
            data = json.loads(r.text)
            if isinstance(data, dict):
                objects = data['results']
            elif isinstance(data, list):
                objects = data
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
        for tid in results.iterkeys():
            doc = None
            if results[tid]:
                doc = results[tid].pop()
            round1.append(doc)
    # remove empties
    round2 = [doc for doc in round1 if doc]
    return round2

def distribute(terms_objects, limit):
    """
    @param terms_objects: list of dicts
    @param limit: int
    """
    termid_objs = {}
    hits = 0
    misses = 0
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

def related_by_topic(term_ids, size):
    """Documents from DDR related to terms.
    
    @param term_ids: list of Topic term IDs.
    @param size: int Number of results per term.
    """
    term_results = {
        tid: _term_documents(tid, size)
        for tid in term_ids
    }
    return term_results
