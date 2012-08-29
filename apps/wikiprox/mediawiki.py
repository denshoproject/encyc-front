from datetime import datetime
import json
import os.path
import re

from bs4 import BeautifulSoup, SoupStrainer, Comment
import requests

from django.conf import settings
from django.core.urlresolvers import reverse

from wikiprox.sources import format_primary_source


def page_data_url(page_title):
    """URL of MediaWiki API call to get page info.
    """
    return '%s?action=parse&format=json' \
           '&page=%s' % (settings.WIKIPROX_MEDIAWIKI_API, page_title)

def lastmod_data_url(page_title):
    """URL of MediaWiki API call to get page revision lastmod.
    """
    return '%s?action=query&format=json&prop=revisions&rvprop=ids|timestamp' \
           '&titles=%s' % (settings.WIKIPROX_MEDIAWIKI_API, page_title)

def page_is_published(pagedata):
    """Indicates whether MediaWiki page contains Category:Published template.
    """
    published = False
    for category in pagedata['parse']['categories']:
        if category['*'] == 'Published':
            published = True
    return published

def page_lastmod(page_title):
    """Retrieves timestamp of last modification.
    """
    lastmod = None
    url = lastmod_data_url(page_title)
    r = requests.get(url)
    if r.status_code == 200:
        pagedata = json.loads(r.text)
        ts = pagedata['query']['pages'].values()[0]['revisions'][0]['timestamp']
        lastmod = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')
    return lastmod

def parse_mediawiki_text(text, images, public=False, printed=False):
    """Parses the body of a MediaWiki page.
    """
    soup = BeautifulSoup(text.replace('<p><br />\n</p>',''))
    soup = remove_staticpage_titles(soup)
    soup = remove_comments(soup)
    soup = remove_edit_links(soup)
    #soup = wrap_sections(soup)
    soup = rewrite_mediawiki_urls(soup)
    soup = rewrite_newpage_links(soup)
    soup = rewrite_prevnext_links(soup)
    if public:
        soup = remove_status_markers(soup)
    if not printed:
        soup = add_top_links(soup)
    primary_sources = find_primary_sources(images)
    soup = remove_primary_sources(soup, primary_sources)
    html = unicode(soup)
    for tag in ['html','body']:
        html = html.replace('<%s>' % tag, '').replace('</%s>' % tag, '')
    return html, primary_sources

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

def wrap_sections(soup):
    """Wraps each <h2> and cluster of <p>s in a <section> tag.
    
    Makes it possible to make certain sections collapsable.
    
    The thing that makes this complicated is that with BeautifulSoup you can't just drop tags into a <div>.  You have to 
    """
    for s in soup.find_all('span', 'mw-headline'):
        # get the <h2> tag
        h = s.parent
        # extract the rest of the section from soup
        siblings = []
        for sibling in h.next_siblings:
            if hasattr(sibling, 'name') and sibling.name == 'h2':
                break
            siblings.append(sibling)
        [sibling.extract() for sibling in siblings]
        # wrap h in a <div>
        div = soup.new_tag('div')
        div['class'] = 'section'
        h = h.wrap(div)
        # append section contents into <div>
        div2 = soup.new_tag('div')
        div2['class'] = 'section_content'
        div2.contents = siblings
        h.append(div2)
    return soup

def remove_status_markers(soup):
    """Remove the "Published", "Needs Primary Sources" tables.
    """
    for d in soup.find_all('div', attrs={'class':'alert'}):
        if 'published' in d['class']:
            d.decompose()
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
    
def find_primary_sources(images):
    """Given list of page images, get the ones with encyclopedia IDs.
    """
    sources = []
    eids = []
    # anything that might be an encyclopedia_id
    for img in images:
        encyclopedia_id = extract_encyclopedia_id(img)
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
            response_objects = response['objects']
            for eid in eids:
                for s in response['objects']:
                    if (eid == s['encyclopedia_id']) and (s not in sources):
                        sources.append(s)
    return sources

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
    
def find_databoxcamps_coordinates(text):
    """Given the raw wikitext, search for coordinates with Databox-Camps.
    
    NOTE: We have some major assumptions here:
    - That there will be only one lng/lat pair in the Databox-Camps.
    - That the lng/lat pair will appear within the Databox-Camps.
    """
    coordinates = []
    if text.find('databox-Camps') > -1:
        lng = None; lat = None;
        for l in re.findall(re.compile('GISLo*ng: (-*[0-9]+.[0-9]+)'), text):
            lng = float(l)
        for l in re.findall(re.compile('GISLat: (-*[0-9]+.[0-9]+)'), text):
            lat = float(l)
        if lng and lat:
            coordinates = (lng,lat)
    return coordinates
    
def add_top_links(soup):
    import copy
    TOPLINK_TEMPLATE = '<div class="toplink"><a href="#top"><i class="icon-chevron-up"></i> Top</a></div>'
    toplink = BeautifulSoup(TOPLINK_TEMPLATE,
                            parse_only=SoupStrainer('div', attrs={'class':'toplink'}))
    n = 0
    for h in soup.find_all('h2'):
        if n > 1:
            h.insert_before(copy.copy(toplink))
        n = n + 1
    soup.append(copy.copy(toplink))
    return soup
