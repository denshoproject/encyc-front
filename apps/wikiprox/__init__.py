import json
import os.path
import re

from bs4 import BeautifulSoup, SoupStrainer, Comment
import requests

from django.conf import settings
from django.core.urlresolvers import reverse

from wikiprox.sources import format_primary_source


def mw_page_is_published(text):
    """Indicates whether MediaWiki page contains Category:Published template.
    """
    published = False
    soup = BeautifulSoup(text, parse_only=SoupStrainer('div', attrs={'class':'mw-content-ltr'}))
    for t in soup.find_all('table', attrs={'class':'published'}):
        published = True
    return published

def mw_page_lastmod(text):
    """Retrieves timestamp of last modification.
    """
    lastmod = None
    soup = BeautifulSoup(text, parse_only=SoupStrainer(id="footer-info-lastmod"))
    return soup.find(id="footer-info-lastmod").contents[0]
    #parts = raw.replace('.','').split('on')
    #ts = parts[1].strip()
    #from dateutils import parser
    #lastmod = parser.parse(ts)
    #return lastmod

def parse_mediawiki_title(text):
    """Parses the title of a MediaWiki page.
    
    Unlike most pages, "static" pages like /index, /about, and /contact
    have their nice titles in <h1> tags.  This normally results in 2 titles
    which is unsightly.
    For pages with 2 <h1> tags, remove the first one.
    """
    title = '[no title]'
    h1s = re.findall('<h1', text)
    if len(h1s) > 1:
        soup = BeautifulSoup(
            text, parse_only=SoupStrainer('div', attrs={'class':'mw-content-ltr'}))
        for t in soup.find_all('span', attrs={'class':'mw-headline'}):
            title = t.string.strip()
    else:
        soup = BeautifulSoup(text, parse_only=SoupStrainer('title'))
        title = soup.title.string.strip().replace(settings.WIKIPROX_MEDIAWIKI_TITLE, '')
    return title

def parse_mediawiki_text(text):
    """Parses the body of a MediaWiki page.
    """
    soup = BeautifulSoup(
        text, parse_only=SoupStrainer('div', attrs={'class':'mw-content-ltr'}))
    soup = remove_staticpage_titles(soup)
    soup = remove_comments(soup)
    soup = remove_edit_links(soup)
    soup = rewrite_mediawiki_urls(soup)
    soup = rewrite_newpage_links(soup)
    soup = rewrite_prevnext_links(soup)
    sources = find_primary_sources(soup)
    #soup = format_primary_sources(soup, sources)
    soup = remove_primary_sources(soup, sources)
    return unicode(soup), sources

def parse_mediawiki_cite_page(text, page, request):
    """Parses the body of a MediaWiki Cite page.
    """
    soup = BeautifulSoup(
        text, parse_only=SoupStrainer('div', attrs={'id':'bodyContent'}))
    # remove stuff
    soup.find(id="contentSub").decompose()
    soup.find(id="jump-to-nav").decompose()
    soup.find(id="specialcite").decompose()
    soup.find(id="catlinks").decompose()
    for d in soup.find_all('div', attrs={'class':'printfooter'}):
        d.decompose()
    for d in soup.find_all('div', attrs={'class':'visualClear'}):
        d.decompose()
    # rewrite URLs
    for a in soup.find_all('a'):
        if page in a['href']:
            url = 'http://%s%s' % (request.META.get('HTTP_HOST',None),
                                   reverse('wikiprox-page', args=[page]))
            a['href'] = a.string = url
    return unicode(soup)

def remove_staticpage_titles(soup):
    """strip extra <h1> on "static" pages

    "Static" pages will have an extra <h1> in the page body.
    This is extracted by parse_mediawiki_title so now we need
    to remove it.
    """
    h1s = soup.find_all('h1')
    if h1s:
        for h1 in soup.find_all('h1'):
            h1.decompose()
    return soup

def remove_comments(soup):
    """TODO Removes MediaWiki comments from page text
    """
    #def iscomment(tag):
    #    return isinstance(text, Comment)
    #comments = soup.findAll(iscomment)
	#[comment.extract() for comment in comments]
    return soup

def remove_edit_links(soup):
    """Removes [edit] spans (ex: <span class="editsection">)
    
    Security precaution: we don't want people to be able to edit, or to find edit links.
    """
    for e in soup.find_all('span', attrs={'class':'editsection'}):
        e.decompose()
    return soup

def rewrite_mediawiki_urls(soup):
    """Rewrites /mediawiki/index.php/... URLs to /...
    """
    for a in soup.find_all('a', href=re.compile('/mediawiki/index.php')):
        a['href'] = a['href'].replace('/mediawiki/index.php', '')
    return soup

def rewrite_newpage_links(soup):
    """Rewrites new-page links
    
    ex: http://.../mediawiki/index.php?title=Nisei&amp;action=edit&amp;redlink=1
    """
    for a in soup.find_all('a', href=re.compile('action=edit')):
        a['href'] = a['href'].replace('?title=', '/')
        a['href'] = a['href'].replace('&action=edit', '')
        a['href'] = a['href'].replace('&redlink=1', '')
    return soup

def rewrite_prevnext_links(soup):
    """Rewrites previous/next links
    
    ex: http://.../mediawiki/index.php?title=Category:Pages_Needing_Primary_Sources&pagefrom=Mary+Oyama+Mittwer
    """
    for a in soup.find_all('a', href=re.compile('pagefrom=')):
        a['href'] = a['href'].replace('?title=', '/')
        a['href'] = a['href'].replace('&pagefrom=', '?pagefrom=')
    for a in soup.find_all('a', href=re.compile('pageuntil=')):
        a['href'] = a['href'].replace('?title=', '/')
        a['href'] = a['href'].replace('&pageuntil=', '?pageuntil=')
    return soup

def extract_encyclopedia_id(uri):
    """Attempts to extract a valid Densho encyclopedia ID from the URI
    
    TODO Check if valid encyclopedia ID
    """
    if 'thumb' in uri:
        path,filename = os.path.split(os.path.dirname(uri))
        eid,ext = os.path.splitext(filename)
    else:
        path,filename = os.path.split(uri)
        eid,ext = os.path.splitext(filename)
    return eid
    
def find_primary_sources(soup):
    """Scan through the soup for <a><img>s and get the ones with encyclopedia IDs.
    """
    sources = []
    imgs = []
    eids = []
    # all the <a><img>s
    for a in soup.find_all('a', attrs={'class':'image'}):
        imgs.append(a.img)
    # anything that might be an encyclopedia_id
    for img in imgs:
        encyclopedia_id = extract_encyclopedia_id(img['src'])
        if encyclopedia_id:
            eids.append(encyclopedia_id)
    # get sources via sources API
    if eids:
        eid_args = []
        for eid in eids:
            eid_args.append('encyclopedia_id__in=%s' % eid)
        url = '%s/primarysource/?%s' % (settings.TANSU_API, '&'.join(eid_args))
        r = requests.get(url, headers={'content-type':'application/json'})
        if r.status_code == 200:
            response = json.loads(r.text)
            for s in response['objects']:
                sources.append(s)
    return sources

def format_primary_sources(soup, sources):
    """Rewrite image HTML so primary sources appear in pop-up lightbox with metadata.
    
    see http://192.168.0.13/redmine/attachments/4/Encyclopedia-PrimarySourceDraftFlow.pdf
    """
    # all the <a><img>s
    contexts = []
    num_sources = 0
    for a in soup.find_all('a', attrs={'class':'image'}):
        num_sources = num_sources + 1
    for a in soup.find_all('a', attrs={'class':'image'}):
        encyclopedia_id = extract_encyclopedia_id(a.img['src'])
        href = None
        if encyclopedia_id and (encyclopedia_id in sources.keys()):
            source = sources[encyclopedia_id]
            template = 'wikiprox/generic.html'
            # rewrite more-info URL
            x,y = a['href'].split('File:')
            eid,ext = os.path.splitext(y)
            href = reverse('wikiprox-source', kwargs={'encyclopedia_id': eid })
        if href:
            img = BeautifulSoup(format_primary_source(source))
            # insert back into page
            a.replace_with(img.body)
    return soup

def remove_primary_sources(soup, sources):
    """Remove primary sources from the MediaWiki page entirely.
    
    see http://192.168.0.13/redmine/attachments/4/Encyclopedia-PrimarySourceDraftFlow.pdf
    ...and really look at it.  Primary sources are all displayed in sidebar_right.
    """
    # all the <a><img>s
    contexts = []
    sources_keys = []
    for s in sources:
        sources_keys.append(s['encyclopedia_id'])
    for a in soup.find_all('a', attrs={'class':'image'}):
        encyclopedia_id = extract_encyclopedia_id(a.img['src'])
        href = None
        if encyclopedia_id and (encyclopedia_id in sources_keys):
            a.decompose()
    return soup
