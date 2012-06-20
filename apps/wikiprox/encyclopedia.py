from datetime import datetime
import json

import requests

from django.conf import settings



def all_pages():
    """Returns a list of all pages, with timestamp of latest revision.
    """
    pages = []
    # all articles
    TS_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
    LIMIT=5000
    url = '%s?action=query&generator=allpages&prop=revisions&rvprop=timestamp&gaplimit=5000&format=json' % (settings.WIKIPROX_MEDIAWIKI_API)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code == 200:
        response = json.loads(r.text)
        if response and response['query'] and response['query']['pages']:
            for id in response['query']['pages']:
                page = response['query']['pages'][id]
                page['timestamp'] = datetime.strptime(page['revisions'][0]['timestamp'], TS_FORMAT)
                pages.append(page)
    return pages

def category_published(namespace_id=None):
    """Returns list of published pages.
    """
    pages = []
    LIMIT=5000
    url = '%s?format=json&action=query&generator=categorymembers&gcmtitle=Category:Published' % settings.WIKIPROX_MEDIAWIKI_API
    if namespace_id:
        url = '%s&gcmnamespace=%s' % (url, namespace_id)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code == 200:
        response = json.loads(r.text)
        if response and response['query'] and response['query']['pages']:
            for id in response['query']['pages']:
                pages.append(response['query']['pages'][id])
    return pages

def namespaces():
    """Returns dict of namespaces and their codes.
    """
    namespaces = {}
    url = '%s?action=query&meta=siteinfo&siprop=namespaces|namespacealiases&format=json' % (settings.WIKIPROX_MEDIAWIKI_API)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code == 200:
        response = json.loads(r.text)
        if response and response['query'] and response['query']['namespaces']:
            for n in response['query']['namespaces']:
                ns = response['query']['namespaces'][n]
                nsid = ns['id']
                if ns.get('canonical',None):
                    nsname = ns['canonical']
                else:
                    nsname = ns['content']
                if not nsname:
                    nsname = u'Default'
                namespaces[nsid] = nsname
    return namespaces

def namespaces_reversed():
    """Returns dict of namespaces and their codes, organized by name.
    """
    nspaces = {}
    for key,val in namespaces().iteritems():
        nspaces[val] = key
    return nspaces

def published_pages():
    """Returns a list of *published* articles (pages), with timestamp of latest revision.
    """
    pages = []
    pids = []  # published_article_ids
    for article in category_published(namespace_id=namespaces_reversed()['Default']):
        pids.append(article['pageid'])
    for article in all_pages():
        if article['pageid'] in pids:
            pages.append(article)
    return pages
