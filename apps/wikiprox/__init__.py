import json
import os.path
import re

from bs4 import BeautifulSoup, SoupStrainer, Comment
import requests

from django.conf import settings
from django.template import Template, Context


def parse_mediawiki_title(text):
    """Parses the title of a MediaWiki page.
    """
    soup = BeautifulSoup(text, parse_only=SoupStrainer('title'))
    return soup.title.string.strip().replace(' - Densho Test Wiki', '')

def parse_mediawiki_text(text):
    """Parses the body of a MediaWiki page.
    """
    soup = BeautifulSoup(
        text, parse_only=SoupStrainer('div', attrs={'class':'mw-content-ltr'}))
    soup = remove_comments(soup)
    soup = remove_edit_links(soup)
    soup = rewrite_mediawiki_urls(soup)
    soup = rewrite_newpage_links(soup)
    sources = find_primary_sources(soup)
    soup = format_images(soup, sources)
    soup = format_video(soup, sources)
    return unicode(soup)


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
    """Rewrites /mediawiki/index.php/... URLs to /wiki/...
    """
    for a in soup.find_all('a', href=re.compile('/mediawiki/index.php')):
        a['href'] = a['href'].replace('/mediawiki/index.php', '/wiki')
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
    sources = {}
    if eids:
        eid_args = []
        for eid in eids:
            eid_args.append('encyclopedia_id__in=%s' % eid)
        url = '%s/primarysource/?%s' % (settings.TANSU_API, '&'.join(eid_args))
        r = requests.get(url, headers={'content-type':'application/json'})
        if r.status_code != 200:
            assert False
        response = json.loads(r.text)
        for s in response['objects']:
            sources[s['encyclopedia_id']] = s
    return sources

IMAGE_TEMPLATE = """
<div class="thumbnail" style="border:4px solid green;">
  <a href="{{ href }}">
    <img src="{{ MEDIA_URL }}{{ src }}"
         alt="{{ caption }} {{ courtesy }}"/>
  </a>
  <br/>
  <span class="caption">
    {{ caption }}
    {{ courtesy }}
  </span>
</div>
"""

def format_images(soup, sources):
    """Rewrite image HTML so images appear in pop-up lightbox with metadata.
    
    - Small, fixed-size thumbnail image
    - Caption text (abbreviated?)
    - Courtesy line
    - Lightbox pop-up code
    - Link to primary source db or digital repository
    see http://192.168.0.13/redmine/attachments/4/Encyclopedia-PrimarySourceDraftFlow.pdf
    """
    # all the <a><img>s
    for a in soup.find_all('a', attrs={'class':'image'}):
        encyclopedia_id = extract_encyclopedia_id(a.img['src'])
        if encyclopedia_id and (encyclopedia_id in sources.keys()):
            source = sources[encyclopedia_id]
            # img src
            if source.get('display',None):
                src = source['display']
            elif source.get('original',None):
                src = source['original']
            src_chopped = src[src.index('sources'):]
            # render
            t = Template(IMAGE_TEMPLATE)
            c = Context({'MEDIA_URL': settings.TANSU_MEDIA_URL,
                         'href': a['href'],
                         'src': src_chopped,
                         'caption': source['caption'],
                         'courtesy': source['courtesy'],})
            img = BeautifulSoup(t.render(c))
            # insert back into page
            a.replace_with(img.body)
    return soup

def format_video(soup, sources):
    """Rewrite image HTML so images appear in pop-up lightbox with player and metadata.
    """
    return soup
