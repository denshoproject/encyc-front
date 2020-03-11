from collections import OrderedDict

from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

from wikiprox import models


@api_view(['GET'])
def articles(request, format=None):
    """DOCUMENTATION GOES HERE.
    """
    data = [
        {
            'title': article.title,
            'url': reverse('wikiprox-api-page', args=([article.url_title]), request=request),
        }
        for article in models.Page.pages()
    ]
    return Response(data)

@api_view(['GET'])
def article(request, url_title, format=None):
    """DOCUMENTATION GOES HERE.
    """
    try:
        page = models.Page.get(url_title)
    except models.NotFoundError:
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
    data = OrderedDict(
        url_title=page.url_title,
        title_sort=page.title_sort,
        links=OrderedDict(
            json=reverse(
                'wikiprox-api-page', args=([page.url_title]), request=request
            ),
            html=reverse(
                'wikiprox-page', args=([page.url_title]), request=request
            ),
        ),
        modified=page.modified,
        title=page.title,
        body=page.body,
        categories=categories,
        sources=sources,
        coordinates=page.coordinates,
        authors=authors,
        ddr_topic_terms=topic_term_ids,
        prev_page=reverse(
            'wikiprox-api-page', args=([page.prev_page]), request=request
        ),
        next_page=reverse(
            'wikiprox-api-page', args=([page.next_page]), request=request
        ),
    )
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
        for author in models.Author.authors()
    ]
    return Response(data)

@api_view(['GET'])
def author(request, url_title, format=None):
    """DOCUMENTATION GOES HERE.
    """
    try:
        author = models.Author.get(url_title)
    except models.NotFoundError:
        return Response(status=status.HTTP_404_NOT_FOUND)
    articles = [
        OrderedDict(
            title=article.title,
            url=reverse('wikiprox-api-page', args=([article.url_title]), request=request),
        )
        for article in author.articles()
    ]
    data = OrderedDict(
        url_title=author.url_title,
        title_sort=author.title_sort,
        links=OrderedDict(
            json=reverse(
                'wikiprox-api-author', args=([author.url_title]), request=request
            ),
            html=reverse(
                'wikiprox-author', args=([author.url_title]), request=request
            ),
        ),
        modified=author.modified,
        title=author.title,
        body=author.body,
        articles=articles,
    )
    return Response(data)


@api_view(['GET'])
def categories(request, format=None):
    """DOCUMENTATION GOES HERE.
    """
    categories = models.Page.pages_by_category()
    assert False
    return Response(data)

@api_view(['GET'])
def category(request, category, format=None):
    """DOCUMENTATION GOES HERE.
    """
    #categories = Backend().categories()
    #articles_by_category = [(key,val) for key,val in categories.items()]
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
        source = models.Source.get(encyclopedia_id)
    except models.NotFoundError:
        return Response(status=status.HTTP_404_NOT_FOUND)
    data = OrderedDict(
        encyclopedia_id=source.encyclopedia_id,
        psms_id=source.psms_id,
        densho_id=source.densho_id,
        institution_id=source.institution_id,
        links=OrderedDict(
            json=reverse(
                'wikiprox-api-source', args=([source.encyclopedia_id]), request=request
            ),
            html=reverse(
                'wikiprox-source', args=([source.encyclopedia_id]), request=request
            ),
        ),
        created=source.created,
        modified=source.modified,
        headword=source.headword,
        caption=source.caption,
        caption_extended=source.caption_extended,
        courtesy=source.courtesy,
        original_path=source.original_path,
        original_url=source.original_url,
        original_size=source.original_size,
        img_size=source.display_size,
        filename=source.filename,
        external_url=source.external_url,
        img_path=source.img_path,
        img_url=source.img_url(),
        streaming_path=source.streaming_path(),
        rtmp_streamer=settings.RTMP_STREAMER,
        rtmp_path=source.streaming_url,
        media_format=source.media_format,
        aspect_ratio=source.aspect_ratio,
        collection_name=source.collection_name,
        transcript_path=source.transcript_path(),
        transcript_url=source.transcript_url(),
        creative_commons=source.creative_commons,
    )
    return Response(data)
