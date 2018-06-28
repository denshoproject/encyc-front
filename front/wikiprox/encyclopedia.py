from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)
from operator import itemgetter
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests

from django.conf import settings
from django.core.cache import cache

from wikiprox import make_cache_key
from wikiprox import mediawiki


NON_ARTICLE_PAGES = ['about', 'categories', 'contact', 'contents', 'search',]
TIMEOUT = float(settings.MEDIAWIKI_API_TIMEOUT)


def api_login_round1(username, password):
    url = '%s?action=login&format=xml' % (settings.MEDIAWIKI_API)
    domain = urlparse(url).netloc
    if domain.find(':') > -1:
        domain = domain.split(':')[0]
    payload = {'lgname':username, 'lgpassword':password}
    r = requests.post(url, data=payload, timeout=TIMEOUT)
    soup = BeautifulSoup(r.text)
    login = soup.find('login')
    result = {
        'result': login['result'],
        'domain': domain,
        'cookieprefix': login['cookieprefix'],
        'sessionid': login['sessionid'],
        'token': login['token'],
        }
    return result

def api_login_round2(username, password, result):
    url = '%s?action=login&format=xml' % (settings.MEDIAWIKI_API)
    domain = urlparse(url).netloc
    if domain.find(':') > -1:
        domain = domain.split(':')[0]
    payload = {'lgname':username, 'lgpassword':password, 'lgtoken':result['token'],}
    cookies = {'%s_session' % result['cookieprefix']: result['sessionid'], 'domain':domain,}
    r = requests.post(url, data=payload, cookies=cookies, timeout=TIMEOUT)
    if 'WrongPass' in r.text:
        raise Exception('Bad MediaWiki API credentials')
    soup = BeautifulSoup(r.text)
    login = soup.find('login')
    result = {
        'result': login['result'],
        'lguserid': login['lguserid'],
        'lgusername': login['lgusername'],
        'lgtoken': login['lgtoken'],
        'cookieprefix': login['cookieprefix'],
        'sessionid': login['sessionid'],
        'domain': domain,
        'cookies': r.cookies,
        }
    return result

def api_login():
    """Tries to perform a MediaWiki API login.
    
    Returns a set of MediaWiki cookies for use by subsequent
    HTTP requests.
    """
    cookies = []
    username = settings.MEDIAWIKI_API_USERNAME
    password = settings.MEDIAWIKI_API_PASSWORD
    round1 = api_login_round1(username, password)
    round2 = api_login_round2(username, password, round1)
    if round2.get('result',None) \
           and (round2['result'] == 'Success') \
           and round2.get('cookies',None):
        cookies = round2['cookies']
    return cookies

def api_logout():
    url = '%s?action=logout' % (settings.MEDIAWIKI_API)
    headers = {'content-type': 'application/json'}
    r = requests.post(url, headers=headers, timeout=TIMEOUT)

def _all_pages(r_text):
    pages = []
    response = json.loads(r_text)
    if response and response['query'] and response['query']['pages']:
        for id in response['query']['pages']:
            page = response['query']['pages'][id]
            page['timestamp'] = page['revisions'][0]['timestamp']
            page.pop('revisions')
            pages.append(page)
    return pages
    
def all_pages():
    """Returns a list of all pages, with timestamp of latest revision.
    """
    cache_key = make_cache_key('wikiprox:encyclopedia:all_pages')
    cached = cache.get(cache_key)
    if cached:
        pages = json.loads(cached)
        for page in pages:
            page['timestamp'] = datetime.strptime(page['timestamp'], mediawiki.TS_FORMAT_ZONED)
    else:
        cookies = api_login()
        # all articles
        LIMIT=5000
        url = '%s?action=query&generator=allpages&prop=revisions&rvprop=timestamp&gaplimit=5000&format=json' % (settings.MEDIAWIKI_API)
        r = requests.get(url, headers={'content-type':'application/json'}, cookies=cookies, timeout=TIMEOUT)
        if r.status_code == 200:
            pages = _all_pages(r.text)
        api_logout()
        cache.set(cache_key, json.dumps(pages), settings.CACHE_TIMEOUT)
    return pages

def _articles_a_z(published_pages, author_pages, nonarticle_titles):
    author_titles = [page['title'] for page in author_pages]
    pages = []
    for page in published_pages:
        if ('Category' not in page['title']) \
        and (page['title'] not in author_titles) \
        and (page['title'] not in nonarticle_titles) \
        and (page['title'] not in pages):
            pages.append(page)
    return pages
    
def articles_a_z():
    """Returns a list of published article titles arranged A-Z.
    """
    cache_key = make_cache_key('wikiprox:encyclopedia:articles_a_z')
    cached = cache.get(cache_key)
    if cached:
        titles = json.loads(cached)
    else:
        titles = _articles_a_z(
            category_members('Published', namespace_id=namespaces_reversed()['Default']),
            published_authors(),
            NON_ARTICLE_PAGES
        )
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
        published = [page['title'] for page in published_pages()]
        cat_titles = [page['title'] for page in category_article_types()]
        for category in cat_titles:
            category = category.replace('Category:','')
            # TODO fix this, this is bad
            titles = [
                page
                for page in category_members(
                        category, namespace_id=namespaces_reversed()['Default']
                )
                if page['title'] in published
            ]
            if titles:
                categories.append(category)
                titles_by_category[category] = titles
        cache.set(cache_key, json.dumps(categories), settings.CACHE_TIMEOUT)
    return categories,titles_by_category

def article_next(title):
    """Returns the title of the next article in the A-Z list.
    """
    titles = [page['title'] for page in articles_a_z()]
    try:
        return titles[titles.index(title) + 1]
    except:
        pass
    return None
    
def article_prev(title):
    """Returns the title of the previous article in the A-Z list.
    """
    titles = [page['title'] for page in articles_a_z()]
    try:
        return titles[titles.index(title) - 1]
    except:
        pass
    return None

def author_articles(title):
    return what_links_here(title)

def _category_members(r_text):
    pages = []
    response = json.loads(r_text)
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
    return pages

def category_members(category_name, namespace_id=None):
    """Returns titles of pages with specified Category: tag.
    
    NOTE: Rather than just returning a list of title strings, this returns
    a list of _dicts_ containing namespace id, title, and sortkey.
    This is so certain views (e.g. Contents A-Z can grab the first letter
    of the title (or sortkey) to use for grouping purposes.
    """
    cache_key = make_cache_key('wikiprox:encyclopedia:category_members:%s:%s' % (category_name, namespace_id))
    cached = cache.get(cache_key)
    if cached:
        pages = json.loads(cached)
    else:
        cookies = api_login()
        LIMIT = 5000
        url = '%s?format=json&action=query&list=categorymembers&cmsort=sortkey&cmprop=ids|sortkeyprefix|title&cmtitle=Category:%s&cmlimit=5000' % (settings.MEDIAWIKI_API, category_name)
        if namespace_id != None:
            url = '%s&gcmnamespace=%s' % (url, namespace_id)
        r = requests.get(url, headers={'content-type':'application/json'}, cookies=cookies, timeout=TIMEOUT)
        if r.status_code == 200:
            pages = _category_members(r.text)
        api_logout()
        cache.set(cache_key, json.dumps(pages), settings.CACHE_TIMEOUT)
    return pages

def category_article_types():
    """Returns list of subcategories underneath 'Article'."""
    titles = [page for page in category_members('Articles')]
    return titles
def category_authors():
    titles = [page for page in category_members('Authors')]
    return titles
def category_supplemental():
    titles = [page for page in category_members('Supplemental_Materials')]
    return titles

def is_article(title):
    titles = [page['title'] for page in published_pages()]
    if title in titles:
        return True
    return False

def is_author(title):
    for page in category_authors():
        if title == page['title']:
            return True
    return False

def _namespaces(r_text):
    namespaces = {}
    response = json.loads(r_text)
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

def namespaces():
    """Returns dict of namespaces and their codes.
    """
    cache_key = make_cache_key('wikiprox:encyclopedia:namespaces')
    cached = cache.get(cache_key)
    if cached:
        namespaces = json.loads(cached)
    else:
        url = '%s?action=query&meta=siteinfo&siprop=namespaces|namespacealiases&format=json' % (settings.MEDIAWIKI_API)
        r = requests.get(url, headers={'content-type':'application/json'}, timeout=TIMEOUT)
        if r.status_code == 200:
            namespaces = _namespaces(r.text)
        cache.set(cache_key, json.dumps(namespaces), settings.CACHE_TIMEOUT)
    return namespaces

def namespaces_reversed():
    """Returns dict of namespaces and their codes, organized by name.
    """
    nspaces = {}
    namespaces_codes = namespaces()
    for key,val in namespaces_codes.iteritems():
        nspaces[val] = key
    return nspaces

def _page_categories(whitelist, r_text):
    categories = []
    article_categories = [c['title'] for c in whitelist]
    response = json.loads(r_text)
    ids = []
    if response and response['query'] and response['query']['pages']:
        ids = [id for id in response['query']['pages'].keys()]
    for id in ids:
        for cat in response['query']['pages'][id]['categories']:
            category = cat['title']
            if article_categories and (category in article_categories):
                categories.append(category.replace('Category:', ''))
    return categories
    
def page_categories(title, whitelist=[]):
    """Returns list of article subcategories the page belongs to.
    """
    cache_key = make_cache_key('wikiprox:encyclopedia:page_categories:%s' % title)
    cached = cache.get(cache_key)
    if cached:
        categories = json.loads(cached)
    else:
        url = '%s?format=json&action=query&prop=categories&titles=%s' % (settings.MEDIAWIKI_API, title)
        r = requests.get(url, headers={'content-type':'application/json'}, timeout=TIMEOUT)
        if r.status_code == 200:
            if not whitelist:
                whitelist = category_article_types()
            categories = _page_categories(whitelist, r.text)
        cache.set(cache_key, json.dumps(categories), settings.CACHE_TIMEOUT)
    return categories

def _published_pages(allpages, all_published_pages):
    # published_article_ids
    pids = [page['pageid'] for page in all_published_pages]
    pages = []
    for page in allpages:
        if page['pageid'] in pids:
            if page.get('revisions') \
            and page['revisions'][0].get('timestamp') \
            and not page.get('timestamp'):
                page['timestamp'] = page['revisions'][0]['timestamp']
            pages.append(page)
    return pages
    
def published_pages(cached_ok=True):
    """Returns a list of *published* articles (pages), with timestamp of latest revision.
    @param cached_ok: boolean Whether cached results are OK.
    """
    cache_key = make_cache_key('wikiprox:encyclopedia:published_pages')
    cached = cache.get(cache_key)
    if cached and cached_ok:
        pages = json.loads(cached)
        for page in pages:
            page['timestamp'] = datetime.strptime(page['timestamp'], mediawiki.TS_FORMAT_ZONED)
    else:
        pages = _published_pages(
            all_pages(),
            category_members('Published', namespace_id=namespaces_reversed()['Default'])
        )
        for page in pages:
            if not isinstance(page['timestamp'], basestring):
                page['timestamp'] = datetime.strftime(page['timestamp'], mediawiki.TS_FORMAT_ZONED)
        cache.set(cache_key, json.dumps(pages), settings.CACHE_TIMEOUT)
    return pages

def _published_authors(publishedpages, categoryauthors):
    titles = []
    for page in publishedpages:
        if page['title'] not in titles:
            titles.append(page['title'])
    authors = [
        page
        for page in categoryauthors
        if page['title'] in titles
    ]
    return authors

def published_authors(cached_ok=True):
    """Returns a list of *published* authors (pages), with timestamp of latest revision.
    @param cached_ok: boolean Whether cached results are OK.
    """
    cache_key = make_cache_key('wikiprox:encyclopedia:published_authors')
    cached = cache.get(cache_key)
    if cached and cached_ok:
        authors = json.loads(cached)
    else:
        authors = _published_authors(
            published_pages(),
            category_authors()
        )
        cache.set(cache_key, json.dumps(authors), settings.CACHE_TIMEOUT)
    return authors

def _whatlinkshere(publishedpages, r_text):
    titles = []
    published = [page['title'] for page in publishedpages]
    response = json.loads(r_text)
    if response and response['query'] and response['query']['backlinks']:
        titles = [
            backlink['title']
            for backlink in response['query']['backlinks']
            if backlink['title'] in published
        ]
    return titles
    
def what_links_here(title):
    """Returns titles of published pages that link to this one.
    """
    cache_key = make_cache_key('wikiprox:encyclopedia:what_links_here:%s' % title)
    cached = cache.get(cache_key)
    if cached:
        titles = json.loads(cached)
    else:
        url = '%s?format=json&action=query&list=backlinks&bltitle=%s&bllimit=5000' % (settings.MEDIAWIKI_API, title)
        r = requests.get(url, headers={'content-type':'application/json'}, timeout=TIMEOUT)
        if r.status_code == 200:
            titles = _whatlinkshere(published_pages(), r.text)
        cache.set(cache_key, json.dumps(titles), settings.CACHE_TIMEOUT)
    return titles
