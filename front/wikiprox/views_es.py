from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_http_methods

from wikiprox import docstore
from wikiprox import models

HOSTS = [{'host':'192.168.56.101', 'port':9200}]
INDEX = 'encyc-dev'




def categories(request, template_name='wikiprox/categories.html'):
    articles = docstore.articles(HOSTS, INDEX)
    return render_to_response(
        template_name,
        {
            'articles_by_category': articles,
        },
        context_instance=RequestContext(request)
    )

def contents(request, template_name='wikiprox/contents.html'):
    articles = docstore.contents(HOSTS, INDEX)
    return render_to_response(
        template_name,
        {
            'articles': articles,
        },
        context_instance=RequestContext(request)
    )

def authors(request, template_name='wikiprox/authors.html'):
    authors = docstore.authors(HOSTS, INDEX)
    authors = models._columnizer(authors, 4)
    return render_to_response(
        template_name,
        {
            'authors': authors,
        },
        context_instance=RequestContext(request)
    )

def author(request, url_title, template_name='wikiprox/author.html'):
    author = docstore.author(HOSTS, INDEX, url_title)
    return render_to_response(
        template_name,
        {
            'page': author,
        },
        context_instance=RequestContext(request)
    )

@require_http_methods(['GET',])
def article(request, url_title='index', printed=False, template_name='wikiprox/page.html'):
    """
    """
    page = docstore.article(HOSTS, INDEX, url_title)
    #if page.error:
    #    raise Http404
    if (not page.published) and (not settings.WIKIPROX_SHOW_UNPUBLISHED):
        template_name = 'wikiprox/unpublished.html'
    elif page.is_author:
        template_name = 'wikiprox/author.html'
    elif page.is_article and page.printed:
        template_name = 'wikiprox/article-print.html'
    else:
        template_name = 'wikiprox/article.html'
    return render_to_response(
        template_name,
        {
            'page': page,
        },
        context_instance=RequestContext(request)
    )
