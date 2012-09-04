from datetime import datetime
import json
from operator import itemgetter

import requests

from django.conf import settings
from django.core.cache import cache

from wikiprox import make_cache_key


NON_ARTICLE_PAGES = ['about', 'categories', 'contact', 'contents', 'search',]
TS_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def all_pages():
    """Returns a list of all pages, with timestamp of latest revision.
    """
    pages = []
    cache_key = make_cache_key('wikiprox:encyclopedia:all_pages')
    cached = cache.get(cache_key)
    if cached:
        pages = json.loads(cached)
        for page in pages:
            page['timestamp'] = datetime.strptime(page['timestamp'], TS_FORMAT)
    else:
        # all articles
        LIMIT=5000
        url = '%s?action=query&generator=allpages&prop=revisions&rvprop=timestamp&gaplimit=5000&format=json' % (settings.WIKIPROX_MEDIAWIKI_API)
        r = requests.get(url, headers={'content-type':'application/json'})
        if r.status_code == 200:
            response = json.loads(r.text)
            if response and response['query'] and response['query']['pages']:
                for id in response['query']['pages']:
                    page = response['query']['pages'][id]
                    page['timestamp'] = page['revisions'][0]['timestamp']
                    pages.append(page)
        cache.set(cache_key, json.dumps(pages), settings.CACHE_TIMEOUT)
    return pages

def articles_a_z():
    """Returns a list of published article titles arranged A-Z.
    """
    titles = []
    cache_key = make_cache_key('wikiprox:encyclopedia:articles_a_z')
    cached = cache.get(cache_key)
    if cached:
        titles = json.loads(cached)
    else:
        authors = []
        [authors.append(page['title']) for page in published_authors()]
        NON_ARTICLE_PAGES.extend(category_authors())
        for page in category_members('Published', namespace_id=namespaces_reversed()['Default']):
            if (page['title'] not in NON_ARTICLE_PAGES) \
                   and ('Category' not in page['title']) \
                   and (page['title'] not in titles) \
                   and (page['title'] not in authors):
                titles.append(page)
        cache.set(cache_key, json.dumps(titles), settings.CACHE_TIMEOUT)
    return titles

def articles_by_category():
    """Returns list of published articles grouped by category.
    """
    categories = []
    titles_by_category = {}
    cache_key = make_cache_key('wikiprox:encyclopedia:articles_by_category')
    cached = cache.get(cache_key)
    if cached:
        categories = json.loads(cached)
    else:
        published = []
        [published.append(page['title']) for page in published_pages()]
        cat_titles = []
        [cat_titles.append(page['title']) for page in category_article_types()]
        for category in cat_titles:
            category = category.replace('Category:','')
            titles = []
            for page in category_members(category,
                                         namespace_id=namespaces_reversed()['Default']):
                if page['title'] in published:
                    titles.append(page)
            if titles:
                categories.append(category)
                titles_by_category[category] = titles
        cache.set(cache_key, json.dumps(categories), settings.CACHE_TIMEOUT)
    return categories,titles_by_category

def article_next(title):
    """Returns the title of the next article in the A-Z list.
    """
    titles = []
    [titles.append(page['title']) for page in articles_a_z()]
    try:
        return titles[titles.index(title) + 1]
    except:
        pass
    return None
    
def article_prev(title):
    """Returns the title of the previous article in the A-Z list.
    """
    titles = []
    [titles.append(page['title']) for page in articles_a_z()]
    try:
        return titles[titles.index(title) - 1]
    except:
        pass
    return None

def author_articles(title):
    return what_links_here(title)

def category_members(category_name, namespace_id=None):
    """Returns titles of pages with specified Category: tag.
    
    Returns list of dicts containing namespace id, title, and sortkey.
    """
    pages = []
    cache_key = make_cache_key('wikiprox:encyclopedia:category_members:%s:%s' % (category_name, namespace_id))
    cached = cache.get(cache_key)
    if cached:
        pages = json.loads(cached)
    else:
        LIMIT = 5000
        url = '%s?format=json&action=query&list=categorymembers&cmsort=sortkey&cmprop=ids|sortkeyprefix|title&cmtitle=Category:%s&cmlimit=5000' % (settings.WIKIPROX_MEDIAWIKI_API, category_name)
        if namespace_id != None:
            url = '%s&gcmnamespace=%s' % (url, namespace_id)
        r = requests.get(url, headers={'content-type':'application/json'})
        if r.status_code == 200:
            response = json.loads(r.text)
            if response and response['query'] and response['query']['categorymembers']:
                for page in response['query']['categorymembers']:
                    page['sortkey'] = page['sortkeyprefix']
                    page.pop('sortkeyprefix')
                    if page['title'] and not page['sortkey']:
                        page['sortkey'] = page['title']
                    if page['sortkey']:
                        page['sortkey'] = page['sortkey'].lower()
                    pages.append(page)
                pages = sorted(pages, key=itemgetter('sortkey'))
        cache.set(cache_key, json.dumps(pages), settings.CACHE_TIMEOUT)
    return pages

def category_article_types():
    """Returns list of subcategories underneath 'Article'."""
    titles = []
    [titles.append(page) for page in category_members('Articles')]
    return titles
def category_authors():
    titles = []
    [titles.append(page) for page in category_members('Authors')]
    return titles
def category_supplemental():
    titles = []
    [titles.append(page) for page in category_members('Supplemental_Materials')]
    return titles

def is_article(title):
    titles = []
    [titles.append(page['title']) for page in published_pages()]
    if title in titles:
        return True
    return False

def is_author(title):
    for page in category_authors():
        if title == page['title']:
            return True
    return False

def namespaces():
    """Returns dict of namespaces and their codes.
    """
    namespaces = {}
    cache_key = make_cache_key('wikiprox:encyclopedia:namespaces')
    cached = cache.get(cache_key)
    if cached:
        namespaces = json.loads(cached)
    else:
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
        cache.set(cache_key, json.dumps(namespaces), settings.CACHE_TIMEOUT)
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
    categories = []
    article_categories = []
    cache_key = make_cache_key('wikiprox:encyclopedia:page_categories:%s' % title)
    cached = cache.get(cache_key)
    if cached:
        categories = json.loads(cached)
    else:
        if not whitelist:
            whitelist = category_article_types()
        [article_categories.append(c['title']) for c in whitelist]
        #
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
        cache.set(cache_key, json.dumps(categories), settings.CACHE_TIMEOUT)
    return categories

def published_pages():
    """Returns a list of *published* articles (pages), with timestamp of latest revision.
    """
    pages = []
    cache_key = make_cache_key('wikiprox:encyclopedia:published_pages')
    cached = cache.get(cache_key)
    if cached:
        pages = json.loads(cached)
        for page in pages:
            page['timestamp'] = datetime.strptime(page['timestamp'], TS_FORMAT)
    else:
        pids = []  # published_article_ids
        for page in category_members('Published', namespace_id=namespaces_reversed()['Default']):
            pids.append(page['pageid'])
        for page in all_pages():
            if page['pageid'] in pids:
                page['timestamp'] = page['revisions'][0]['timestamp']
                pages.append(page)
        cache.set(cache_key, json.dumps(pages), settings.CACHE_TIMEOUT)
    return pages

def published_authors():
    """Returns a list of *published* authors (pages), with timestamp of latest revision.
    """
    cache_key = make_cache_key('wikiprox:encyclopedia:published_authors')
    cached = cache.get(cache_key)
    if cached:
        published_authors = json.loads(cached)
    else:
        published_authors = []
        titles = []
        for page in published_pages():
            if page['title'] not in titles:
                titles.append(page['title'])
        for page in category_authors():
            if page['title'] in titles:
               published_authors.append(page)
        cache.set(cache_key, json.dumps(published_authors), settings.CACHE_TIMEOUT)
    return published_authors

def what_links_here(title):
    """Returns titles of published pages that link to this one.
    """
    titles = []
    cache_key = make_cache_key('wikiprox:encyclopedia:what_links_here:%s' % title)
    cached = cache.get(cache_key)
    if cached:
        titles = json.loads(cached)
    else:
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
        cache.set(cache_key, json.dumps(titles), settings.CACHE_TIMEOUT)
    return titles
