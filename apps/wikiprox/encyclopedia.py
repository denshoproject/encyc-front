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
    NON_ARTICLE_PAGES.extend(category_authors())
    for page in category_members('Published', namespace_id=namespaces_reversed()['Default']):
        if (page['title'] not in NON_ARTICLE_PAGES) \
               and ('Category' not in page['title']) \
               and (page['title'] not in titles):
            titles.append(page['title'])
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

def author_articles(title):
    return what_links_here(title)

def category_members(category_name, namespace_id=None):
    """Returns titles of pages with specified Category: tag.
    """
    pages = []
    LIMIT = 5000
    url = '%s?format=json&action=query&list=categorymembers&cmtitle=Category:%s&cmlimit=5000' % (settings.WIKIPROX_MEDIAWIKI_API, category_name)
    if namespace_id != None:
        url = '%s&gcmnamespace=%s' % (url, namespace_id)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code == 200:
        response = json.loads(r.text)
        if response and response['query'] and response['query']['categorymembers']:
            for page in response['query']['categorymembers']:
                pages.append(page)
    return pages

def category_article_types():
    """Returns list of subcategories underneath 'Article'."""
    titles = []
    [titles.append(page['title']) for page in category_members('Articles')]
    return titles
def category_authors():
    titles = []
    [titles.append(page['title']) for page in category_members('Authors')]
    return titles
def category_supplemental():
    titles = []
    [titles.append(page['title']) for page in category_members('Supplemental_Materials')]
    return titles

def is_article(title):
    titles = []
    [titles.append(page['title']) for page in published_pages()]
    if title in titles:
        return True
    return False

def is_author(title):
    if title in category_authors():
        return True
    return False

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

def page_categories(title, whitelist=[]):
    """Returns list of article subcategories the page belongs to.
    """
    article_categories = []
    if not whitelist:
        whitelist = category_article_types()
    [article_categories.append(c) for c in whitelist]
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
                category = cat['title']
                if article_categories and (category in article_categories):
                    categories.append(category.replace('Category:', ''))
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
    """Returns titles of published pages that link to this one.
    """
    titles = []
    #
    published = []
    [published.append(page['title']) for page in published_pages()]
    #
    url = '%s?format=json&action=query&list=backlinks&bltitle=%s&bllimit=5000' % (settings.WIKIPROX_MEDIAWIKI_API, title)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code == 200:
        response = json.loads(r.text)
        if response and response['query'] and response['query']['backlinks']:
            for backlink in response['query']['backlinks']:
                if backlink['title'] in published:
                    titles.append(backlink['title'])
    return titles
