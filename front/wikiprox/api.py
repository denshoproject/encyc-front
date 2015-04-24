from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

from wikiprox.models import Elasticsearch as Backend


@api_view(['GET'])
def articles(request, format=None):
    """DOCUMENTATION GOES HERE.
    """
    data = [
        {
            'title': article.title,
            'url': reverse('wikiprox-api-page', args=([article.url_title]), request=request),
        }
        for article in Backend().articles()
    ]
    return Response(data)

@api_view(['GET'])
def article(request, url_title, format=None):
    """DOCUMENTATION GOES HERE.
    """
    page = Backend().page(url_title)
    if not page:
        return Response(status=status.HTTP_404_NOT_FOUND)
    sources = [
        reverse('wikiprox-api-source', args=([encyc_id]), request=request)
        for encyc_id in page.sources
    ]
    topic_term_ids = [
        '%s/facet/topics/%s/objects/' % (settings.DDRPUBLIC_API, term['id'])
        for term in page.topics()
    ]
    categories = [
        reverse('wikiprox-api-category', args=([category]), request=request)
        for category in page.categories
    ]
    author_articles = [
        reverse('wikiprox-api-page', args=([title]), request=request)
        for title in page.author_articles
    ]
    data = {
        'url_title': page.url_title,
        'url': reverse('wikiprox-api-page', args=([page.url_title]), request=request),
        'absolute_url': reverse('wikiprox-page', args=([page.url_title]), request=request),
        'lastmod': page.lastmod,
        'title_sort': page.title_sort,
        'title': page.title,
        'body': page.body,
        'categories': categories,
        'author_articles': author_articles,
        'coordinates': page.coordinates,
        'prev_page': reverse('wikiprox-api-page', args=([page.prev_page]), request=request),
        'next_page': reverse('wikiprox-api-page', args=([page.next_page]), request=request),
        'sources': sources,
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
        for author in sorted(
            Backend().authors(),
            key=lambda a: a.title_sort.lower()
        )
    ]
    return Response(data)

@api_view(['GET'])
def author(request, url_title, format=None):
    """DOCUMENTATION GOES HERE.
    """
    author = Backend().author(url_title)
    articles = [
        {
            'title': article.title,
            'url': reverse('wikiprox-api-page', args=([article.url_title]), request=request),
        }
        for article in [
            Backend().page(t) for t in author.author_articles
        ]
    ]
    data = {
        'url_title': author.url_title,
        'url': reverse('wikiprox-api-author', args=([author.url_title]), request=request),
        'absolute_url': reverse('wikiprox-author', args=([author.url_title]), request=request),
        'title': author.title,
        'title_sort': author.title_sort,
        'body': author.body,
        'lastmod': author.lastmod,
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
    source = Backend().source(encyclopedia_id)
    data = {
        'encyclopedia_id': source.encyclopedia_id,
        'psms_id': source.psms_id,
        'densho_id': source.densho_id,
        'institution_id': source.institution_id,
        'url': reverse('wikiprox-api-source', args=([source.encyclopedia_id]), request=request),
        'absolute_url': reverse('wikiprox-source', args=([source.encyclopedia_id]), request=request),
        'streaming_url': source.streaming_url,
        'external_url': source.external_url,
        'original': source.original,
        'original_size': source.original_size,
        'img_url': source.display,
        'img_size': source.display_size,
        'thumbnail_lg': source.thumbnail_lg,
        'thumbnail_sm': source.thumbnail_sm,
        'media_format': source.media_format,
        'aspect_ratio': source.aspect_ratio,
        'title': source.title,
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
        'rtmp_streamer': source.rtmp_streamer,
    }
    return Response(data)
