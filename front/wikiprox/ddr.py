"""front.ddr -- Links to the DDR REST API
"""

import requests

from django.conf import settings


def _term_documents(term_id, size):
    """Get objects for specified term from DDR REST API.
    
    @param term_id: int
    @param size: int Maximum number of results to return.
    @returns: list of dicts
    """
    url = 'http://192.168.56.120/api/0.1/facet/topics/%s/objects/' % term_id
    r = requests.get(url)
    if (r.status_code == 200) and ('json' in r.headers['content-type']):
        documents = r.json['results']
    else:
        documents = []
    return documents

def _balance(results, size):
    """cycle through term IDs taking one at a time until we have enough
    
    @param results: dict of search results keyed to term IDs.
    @param size: int Maximum number of results to return.
    """
    round1 = []
    while(len(round1) < size):
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
