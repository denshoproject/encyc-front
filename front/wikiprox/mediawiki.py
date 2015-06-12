from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)
import os
import re

from bs4 import BeautifulSoup, SoupStrainer, Comment
import requests

from django.conf import settings

TS_FORMAT = '%Y-%m-%dT%H:%M:%S'
TS_FORMAT_ZONED = '%Y-%m-%dT%H:%M:%SZ'
TIMEOUT = float(settings.WIKIPROX_MEDIAWIKI_API_TIMEOUT)


def page_data_url(api_url, page_title):
    """URL of MediaWiki API call to get page info.
    
    @parap api_url: str Base URL for MediaWiki API.
    @param page_title: Page title from MediaWiki URL.
    @returns: url
    """
    url = '%s?action=parse&format=json&page=%s'
    return url % (api_url, page_title)

def lastmod_data_url(api_url, page_title):
    """URL of MediaWiki API call to get page revision lastmod.
    
    @parap api_url: str Base URL for MediaWiki API.
    @param page_title: Page title from MediaWiki URL.
    @returns: url
    """
    url = '%s?action=query&format=json&prop=revisions&rvprop=ids|timestamp&titles=%s'
    return url % (api_url, page_title)

def page_is_published(pagedata):
    """Indicates whether page contains Category:Published template.
    
    @param pagedata: dict Output of API call.
    @returns: Boolean
    """
    published = False
    for category in pagedata['parse']['categories']:
        if category['*'] == 'Published':
            published = True
    return published

def page_lastmod(api_url, page_title):
    """Retrieves timestamp of last modification.
    
    @parap api_url: str Base URL for MediaWiki API.
    @param page_title: Page title from MediaWiki URL.
    @returns: datetime or None
    """
    lastmod = None
    url = lastmod_data_url(api_url, page_title)
    logging.debug(url)
    r = requests.get(url, timeout=TIMEOUT)
    if r.status_code == 200:
        pagedata = json.loads(r.text)
        ts = pagedata['query']['pages'].values()[0]['revisions'][0]['timestamp']
        lastmod = datetime.strptime(ts, TS_FORMAT_ZONED)
    return lastmod

def parse_mediawiki_text(text, primary_sources, public=False, printed=False):
    """Parses the body of a MediaWiki page.
    
    @param text: str HTML contents of page body.
    @param primary_sources: list
    @param public: Boolean
    @param printed: Boolean
    @returns: html, list of primary sources
    """
    soup = BeautifulSoup(text.replace('<p><br />\n</p>',''))
    soup = remove_staticpage_titles(soup)
    soup = remove_comments(soup)
    soup = remove_edit_links(soup)
    #soup = wrap_sections(soup)
    soup = rewrite_newpage_links(soup)
    soup = rewrite_prevnext_links(soup)
    soup = remove_status_markers(soup)
    if not printed:
        soup = add_top_links(soup)
    soup = remove_primary_sources(soup, primary_sources)
    html = unicode(soup)
    html = rewrite_mediawiki_urls(html)
    for tag in ['html','body']:
        html = html.replace('<%s>' % tag, '').replace('</%s>' % tag, '')
    return html

def remove_staticpage_titles(soup):
    """strip extra <h1> on "static" pages
    
    Called by parse_mediawiki_text.
    "Static" pages will have an extra <h1> in the page body.
    This is extracted by parse_mediawiki_title so now we need
    to remove it.
    
    @param soup: BeautifulSoup object
    @returns: soup
    """
    h1s = soup.find_all('h1')
    if h1s:
        for h1 in soup.find_all('h1'):
            h1.decompose()
    return soup

def remove_comments(soup):
    """TODO Removes MediaWiki comments from page text
    
    Called by parse_mediawiki_text.
    
    @param soup: BeautifulSoup object
    @returns: soup
    """
    #def iscomment(tag):
    #    return isinstance(text, Comment)
    #comments = soup.findAll(iscomment)
	#[comment.extract() for comment in comments]
    return soup

def remove_edit_links(soup):
    """Removes [edit] spans (ex: <span class="editsection">)
    
    Called by parse_mediawiki_text.
    Security precaution: we don't want people to be able to edit,
    or to find edit links.
    
    @param soup: BeautifulSoup object
    @returns: soup
    """
    for e in soup.find_all('span', attrs={'class':'mw-editsection'}):
        e.decompose()
    return soup

def wrap_sections(soup):
    """Wraps each <h2> and cluster of <p>s in a <section> tag.
    
    Called by parse_mediawiki_text.
    Makes it possible to make certain sections collapsable.
    The thing that makes this complicated is that with BeautifulSoup
    you can't just drop tags into a <div>.  You have to 
    
    @param soup: BeautifulSoup object
    @returns: soup
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
    
    Called by parse_mediawiki_text.
    
    @param soup: BeautifulSoup object
    @returns: soup
    """
    for d in soup.find_all('div', attrs={'class':'alert'}):
        if 'published' in d['class']:
            d.decompose()
    return soup

def rewrite_mediawiki_urls(html):
    """Removes /mediawiki/index.php stub from URLs
    
    Called by parse_mediawiki_text.
    
    @param html: str
    @returns: html
    """
    PATTERNS = [
        '/mediawiki/index.php',
        '/mediawiki',
    ]
    for pattern in PATTERNS:
        html = re.sub(pattern, '', html)
    return html

def rewrite_newpage_links(soup):
    """Rewrites new-page links
    
    Called by parse_mediawiki_text.
    ex: http://.../mediawiki/index.php?title=Nisei&amp;action=edit&amp;redlink=1
    
    @param soup: BeautifulSoup object
    @returns: soup
    """
    for a in soup.find_all('a', href=re.compile('action=edit')):
        a['href'] = a['href'].replace('?title=', '/')
        a['href'] = a['href'].replace('&action=edit', '')
        a['href'] = a['href'].replace('&redlink=1', '')
    return soup

def rewrite_prevnext_links(soup):
    """Rewrites previous/next links
    
    Called by parse_mediawiki_text.
    ex: http://.../mediawiki/index.php?title=Category:Pages_Needing_Primary_Sources&pagefrom=Mary+Oyama+Mittwer
    
    @param soup: BeautifulSoup object
    @returns: soup
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
    
    @param uri: str
    @returns: eid
    """
    if 'thumb' in uri:
        path,filename = os.path.split(os.path.dirname(uri))
        eid,ext = os.path.splitext(filename)
    else:
        path,filename = os.path.split(uri)
        eid,ext = os.path.splitext(filename)
    return eid
    
def find_primary_sources(api_url, images):
    """Given list of page images, get the ones with encyclopedia IDs.
    
    Called by parse_mediawiki_text.
    
    @param api_url: SOURCES_URL
    @param images: list
    @returns: list of sources
    """
    logging.debug('find_primary_sources(%s, %s)' % (api_url, images))
    logging.debug('looking for %s' % len(images))    
    sources = []
    eids = []
    # anything that might be an encyclopedia_id
    for img in images:
        encyclopedia_id = extract_encyclopedia_id(img)
        if encyclopedia_id:
            eids.append(encyclopedia_id)
    # get sources via sources API
    if eids:
        eid_args = ['encyclopedia_id__in=%s' % eid for eid in eids]
        url = '%s/primarysource/?%s' % (api_url, '&'.join(eid_args))
        r = requests.get(url, headers={'content-type':'application/json'}, timeout=TIMEOUT)
        if r.status_code == 200:
            response = json.loads(r.text)
            response_objects = response['objects']
            for eid in eids:
                for s in response['objects']:
                    if (eid == s['encyclopedia_id']) and (s not in sources):
                        sources.append(s)
    logging.debug('retrieved %s' % len(sources))
    return sources

def remove_primary_sources(soup, sources):
    """Remove primary sources from the MediaWiki page entirely.
    
    Called by parse_mediawiki_text.
    see http://192.168.0.13/redmine/attachments/4/Encyclopedia-PrimarySourceDraftFlow.pdf
    ...and really look at it.  Primary sources are all displayed in sidebar_right.
    
    @param soup: BeautifulSoup object
    @param sources: list
    @returns: soup
    """
    # all the <a><img>s
    contexts = []
    sources_keys = [s['encyclopedia_id'] for s in sources]
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
    
    @param text: str HTML
    @returns: list of coordinate tuples (lng,lat)
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
    """Adds ^top links at the end of page sections.
    
    Called by parse_mediawiki_text.
    
    @param soup: BeautifulSoup object
    @returns: soup
    """
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

def find_author_info(text):
    """Given raw HTML, extract author display and citation formats.
    
    Example 1:
    <div id="authorByline">
      <b>
        Authored by
        <a href="/Tom_Coffman" title="Tom Coffman">Tom Coffman</a>
      </b>
    </div>
    <div id="citationAuthor" style="display:none;">
      Coffman, Tom
    </div>
    
    Example 2:
    <div id="authorByline">
      <b>
        Authored by
        <a href="/mediawiki/index.php/Jane_L._Scheiber" title="Jane L. Scheiber">Jane L. Scheiber</a>
        and
        <a href="/mediawiki/index.php/Harry_N._Scheiber" title="Harry N. Scheiber">Harry N. Scheiber</a>
      </b>
    </div>
    <div id="citationAuthor" style="display:none;">
      Scheiber,Jane; Scheiber,Harry
    </div>
    
    @param text: str HTML
    @returns: dict of authors
    """
    authors = {'display':[], 'parsed':[],}
    soup = BeautifulSoup(text.replace('<p><br />\n</p>',''))
    for byline in soup.find_all('div', id='authorByline'):
        for a in byline.find_all('a'):
            if hasattr(a,'contents') and a.contents:
                authors['display'].append(a.contents[0])
    for citation in soup.find_all('div', id='citationAuthor'):
        if hasattr(citation,'contents') and citation.contents:
            names = []
            for n in citation.contents[0].split(';'):
                if 'and' in n:
                    for name in n.split('and'):
                        names.append(name.strip())
                else:
                    names.append(n)
            for n in names:
                try:
                    surname,givenname = n.strip().split(',')
                    name = [surname.strip(), givenname.strip()]
                except:
                    name = [n,]
                    logging.error(n)
                    logging.error('mediawiki.find_author_info')
                    logging.error('ValueError: too many values to unpack')
                authors['parsed'].append(name)
    return authors
