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
        url = '%s/facet/topics/%s/objects/?%s=1' % (
            settings.DDRPUBLIC_API, term_id, settings.DDRPUBLIC_LOCAL_MEDIA_MARKER)
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

def related_by_topic(term_ids, size, balanced=False):
    """Documents from DDR related to terms.
    
    @param term_ids: list of Topic term IDs.
    @param size: int Maximum number of results to return.
    """
    term_results = {
        tid: _term_documents(tid, size)
        for tid in term_ids
    }
    if balanced:
        return _balance(term_results, size)
    return term_results
