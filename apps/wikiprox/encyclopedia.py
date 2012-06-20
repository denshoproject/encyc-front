from datetime import datetime
import json

import requests

from django.conf import settings



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

def category_published(namespace_id=namespaces_reversed()['Default']):
    """Returns list of published pages.
    """
    pages = []
    LIMIT=5000
    url = '%s?action=query&generator=categorymembers&gcmtitle=Category:Published&gcmnamespace=%s&format=json' % (settings.WIKIPROX_MEDIAWIKI_API, namespace_id)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code == 200:
        response = json.loads(r.text)
        if response and response['query'] and response['query']['pages']:
            for id in response['query']['pages']:
                p = response['query']['pages'][id]
                page = {}
                page['id'] = p['pageid']
                page['title'] = p['title']
                page['location'] = '/wiki/%s/' % p['title']
                pages.append(page)
    return pages

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
            ids = []
            for id  in response['query']['pages'].keys():
                if id not in ids:
                    ids.append(id)
            for id in ids:
                p = response['query']['pages'][id]
                page = {}
                page['id'] = p['pageid']
                page['title'] = p['title']
                page['location'] = '/wiki/%s/' % p['title']
                page['timestamp'] = datetime.strptime(p['revisions'][0]['timestamp'], TS_FORMAT)
                pages.append(page)
    return pages

def published_pages():
    """Returns a list of *published* articles (pages), with timestamp of latest revision.
    """
    pages = []
    pids = []  # published_article_ids
    for article in category_published():
        pids.append(article['id'])
    for article in all_pages():
        if article['id'] in pids:
            pages.append(article)
    return pages
