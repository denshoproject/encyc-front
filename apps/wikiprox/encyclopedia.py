from datetime import datetime
import json

import requests

from django.conf import settings



NON_ARTICLE_PAGES = ['about', 'contact', 'search',]


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


def articles_a_z():
    """Returns a list of published article titles arranged A-Z.
    
    TODO: display people according to last name
    """
    titles = []
    for article in category_members('Published', namespace_id=namespaces_reversed()['Default']):
        if (article['title'] not in NON_ARTICLE_PAGES) and (article['title'] not in titles):
            titles.append(article['title'])
    titles.sort()
    return titles

def article_next(title):
    """Returns the title of the next article in the A-Z list.
    """
    titles = articles_a_z()
    try:
        return titles[titles.index(title) + 1]
    except:
        pass
    return None
    

def article_prev(title):
    """Returns the title of the previous article in the A-Z list.
    """
    titles = articles_a_z()
    try:
        return titles[titles.index(title) - 1]
    except:
        pass
    return None

def category_members(category_name, namespace_id=None):
    """Returns list of pages with specified Category: tag.
    
    TODO: can we just return the category names?
    """
    pages = []
    LIMIT=5000
    url = '%s?format=json&action=query&generator=categorymembers&gcmtitle=Category:%s' % (settings.WIKIPROX_MEDIAWIKI_API, category_name)
    if namespace_id != None:
        url = '%s&gcmnamespace=%s' % (url, namespace_id)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code == 200:
        response = json.loads(r.text)
        if response and response['query'] and response['query']['pages']:
            for id in response['query']['pages']:
                pages.append(response['query']['pages'][id])
    return pages

def category_article_types():
    return category_members('Articles')
def category_authors():
    return category_members('Authors')
def category_supplemental():
    return category_members('Supplemental_Materials')

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

def page_categories(title, whitelist=category_article_types()):
    """Returns list of article subcategories the page belongs to.
    """
    article_categories = []
    for c in whitelist:
        article_categories.append(c['title'].replace('Category:', ''))
    #
    categories = []
    url = '%s?format=json&action=query&prop=categories&titles=%s' % (settings.WIKIPROX_MEDIAWIKI_API, title)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code == 200:
        response = json.loads(r.text)
        ids = []
        if response and response['query'] and response['query']['pages']:
            for id in response['query']['pages'].keys():
                ids.append(id)
        for id in ids:
            for cat in response['query']['pages'][id]['categories']:
                category = cat['title'].replace('Category:', '')
                if article_categories and (category in article_categories):
                    categories.append(category)
    return categories

def published_pages():
    """Returns a list of *published* articles (pages), with timestamp of latest revision.
    """
    pages = []
    pids = []  # published_article_ids
    for article in category_members('Published', namespace_id=namespaces_reversed()['Default']):
        pids.append(article['pageid'])
    for article in all_pages():
        if article['pageid'] in pids:
            pages.append(article)
    return pages

def what_links_here(title):
    """Returns titles of pages that link to this one.
    """
    titles = []
    url = '%s?format=json&action=query&list=backlinks&bltitle=%s' % (settings.WIKIPROX_MEDIAWIKI_API, title)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code == 200:
        response = json.loads(r.text)
        if response and response['query'] and response['query']['backlinks']:
            for backlink in response['query']['backlinks']:
                titles.append(backlink['title'])
    return titles
