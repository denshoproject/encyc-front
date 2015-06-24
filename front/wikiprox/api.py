from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

from wikiprox.models import Elasticsearch as Backend
from wikiprox.models import Page, Source, Author
from wikiprox.models import MAX_SIZE, NotFoundError


@api_view(['GET'])
def articles(request, format=None):
    """DOCUMENTATION GOES HERE.
    """
    data = [
        {
            'title': article.title,
            'url': reverse('wikiprox-api-page', args=([article.url_title]), request=request),
        }
        for article in Page.pages()
    ]
    return Response(data)

@api_view(['GET'])
def article(request, url_title, format=None):
    """DOCUMENTATION GOES HERE.
    """
    try:
        page = Page.get(url_title)
        page.scrub()
    except NotFoundError:
        return Response(status=status.HTTP_404_NOT_FOUND)
    categories = [
        reverse('wikiprox-api-category', args=([category]), request=request)
        for category in page.categories
    ]
    sources = [
        reverse('wikiprox-api-source', args=([source_id]), request=request)
        for source_id in page.source_ids
    ]
    topic_term_ids = [
        '%s/facet/topics/%s/objects/' % (settings.DDR_API, term['id'])
        for term in page.topics()
    ]
    authors = [
        reverse('wikiprox-api-author', args=([author_titles]), request=request)
        for author_titles in page.authors_data['display']
    ]
    data = {
        'url_title': page.url_title,
        'url': reverse('wikiprox-api-page', args=([page.url_title]), request=request),
        'absolute_url': reverse('wikiprox-page', args=([page.url_title]), request=request),
        'modified': page.modified,
        'title_sort': page.title_sort,
        'prev_page': reverse('wikiprox-api-page', args=([page.prev_page]), request=request),
        'next_page': reverse('wikiprox-api-page', args=([page.next_page]), request=request),
        'title': page.title,
        'body': page.body,
        'categories': categories,
        'sources': sources,
        'coordinates': page.coordinates,
        'authors': authors,
        'ddr_topic_terms': topic_term_ids,
    }
    return Response(data)


@api_view(['GET'])
def authors(request, format=None):
    """DOCUMENTATION GOES HERE.
    """
    data = [
        {
            'title': author.title,
            'title_sort': author.title_sort,
            'url': reverse('wikiprox-api-author', args=([author.url_title]), request=request),
        }
        for author in Author.authors()
    ]
    return Response(data)

@api_view(['GET'])
def author(request, url_title, format=None):
    """DOCUMENTATION GOES HERE.
    """
    try:
        author = Author.get(url_title)
    except NotFoundError:
        return Response(status=status.HTTP_404_NOT_FOUND)
    articles = [
        {
            'title': article.title,
            'url': reverse('wikiprox-api-page', args=([article.url_title]), request=request),
        }
        for article in author.articles()
    ]
    data = {
        'url_title': author.url_title,
        'url': reverse('wikiprox-api-author', args=([author.url_title]), request=request),
        'absolute_url': reverse('wikiprox-author', args=([author.url_title]), request=request),
        'title': author.title,
        'title_sort': author.title_sort,
        'body': author.body,
        'modified': author.modified,
        'articles': articles,
    }
    return Response(data)


@api_view(['GET'])
def categories(request, format=None):
    """DOCUMENTATION GOES HERE.
    """
    categories = Backend().categories()
    assert False
    return Response(data)

@api_view(['GET'])
def category(request, category, format=None):
    """DOCUMENTATION GOES HERE.
    """
    #categories = Backend().categories()
    #articles_by_category = [(key,val) for key,val in categories.iteritems()]
    assert False
    data = {}
    return Response(data)


@api_view(['GET'])
def sources(request, format=None):
    # can't browse sources independent of articles
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def source(request, encyclopedia_id, format=None):
    """DOCUMENTATION GOES HERE.
    """
    try:
        source = Source.get(encyclopedia_id)
    except NotFoundError:
        return Response(status=status.HTTP_404_NOT_FOUND)
    data = {
        'encyclopedia_id': source.encyclopedia_id,
        'psms_id': source.psms_id,
        'densho_id': source.densho_id,
        'institution_id': source.institution_id,
        'url': reverse('wikiprox-api-source', args=([source.encyclopedia_id]), request=request),
        'absolute_url': reverse('wikiprox-source', args=([source.encyclopedia_id]), request=request),
        'streaming_url': source.streaming_url,
        'external_url': source.external_url,
        'original_url': source.original_url,
        'original_size': source.original_size,
        'img_url': source.display,
        'img_size': source.display_size,
        'filename': source.filename,
        'img_path': source.img_path,
        'img_url': source.img_url,
        'media_format': source.media_format,
        'aspect_ratio': source.aspect_ratio,
        'collection_name': source.collection_name,
        'headword': source.headword,
        'caption': source.caption,
        'caption_extended': source.caption_extended,
        'transcript': source.transcript,
        'courtesy': source.courtesy,
        'creative_commons': source.creative_commons,
        'created': source.created,
        'modified': source.modified,
        'published': source.published,
        'rtmp_streamer': settings.RTMP_STREAMER,
    }
    return Response(data)
