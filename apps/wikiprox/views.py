from datetime import datetime, timedelta
import re

from bs4 import BeautifulSoup, SoupStrainer
from bs4 import Comment
import requests
import simplejson

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.http import require_http_methods




@require_http_methods(['GET',])
def page(request, page, template_name='wikiprox/page.html'):
    """
    Alternatives to BeautifulSoup:
    - basic string-split
    - regex
    """
    # API seems to not return page contents
    #url = '%s%s?format=txt' % (settings.WIKIPROX_MEDIAWIKI_API, page)
    url = '%s/%s' % (settings.WIKIPROX_MEDIAWIKI_HTML, page)
    r = requests.get(url)
    if r.status_code != 200:
        assert False
    
    tsoup = BeautifulSoup(r.text, parse_only=SoupStrainer('title'))
    title = tsoup.title.string.strip()
    title = title.replace(' - Densho Test Wiki', '')
    soup = BeautifulSoup(
        r.text,
        parse_only=SoupStrainer('div', attrs={'class':'mw-content-ltr'}))
    
    ## TODO remove comments (doesn't seem to work...)
    #def iscomment(tag):
    #    return isinstance(text, Comment)
    #comments = soup.findAll(iscomment)
	#[comment.extract() for comment in comments]
    
    # rm [edit] spans (ex: <span class="editsection">)
    for e in soup.find_all('span', attrs={'class':'editsection'}):
        e.decompose()
    
    # rewrite /mediawiki/index.php/... URLs to /wiki/...
    for a in soup.find_all('a', href=re.compile('/mediawiki/index.php')):
        a['href'] = a['href'].replace('/mediawiki/index.php', '/wiki')
    
    # rewrite new-page links
    # ex: http://.../mediawiki/index.php?title=Nisei&amp;action=edit&amp;redlink=1"
    for a in soup.find_all('a', href=re.compile('action=edit')):
        a['href'] = a['href'].replace('?title=', '/')
        a['href'] = a['href'].replace('&action=edit', '')
        a['href'] = a['href'].replace('&redlink=1', '')
    
    return render_to_response(
        template_name,
        {'title': title,
         'bodycontent': unicode(soup),},
        context_instance=RequestContext(request)
    )


@require_http_methods(['GET',])
def media(request, filename, template_name='wikiprox/mediafile.html'):
    """
    """
    mediafile = None
    url = '%s/imagefile/?uri=tansu/%s' % (settings.TANSU_API, filename)
    r = requests.get(url, headers={'content-type':'application/json'})
    if r.status_code != 200:
        assert False
    response = simplejson.loads(r.text)
    if response and (response['meta']['total_count'] == 1):
        mediafile = response['objects'][0]
    return render_to_response(
        template_name,
        {'mediafile': mediafile,
         'media_url': settings.TANSU_MEDIA_URL,},
        context_instance=RequestContext(request)
    )


@require_http_methods(['GET',])
def index(request):
    pass
