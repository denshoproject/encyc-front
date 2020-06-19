from django.views.generic import TemplateView
from django.contrib.sitemaps import views as sitemap_views
from django.urls import include, path, re_path

#from django.contrib import admin
#admin.autodiscover()

from front import api as front_api
from events import api as events_api
from events import views as events_views
from locations import api as locations_api
from locations import views as locations_views
from wikiprox import api as wiki_api
from wikiprox import views as wiki_views
from wikiprox.sitemaps import MediaWikiSitemap, SourceSitemap
sitemaps = {
    'wiki': MediaWikiSitemap,
    'sources': SourceSitemap,
}

urlpatterns = [
    #path('admin/', include(admin.site.urls)),
    #re_path(r'^api/0.1/urls-titles/$', wiki_views.api_contents, name='wikiprox-api-contents'),
    re_path(r"^api/0.1/articles/(?P<url_title>[\w\W]+)/$", wiki_api.article, name='wikiprox-api-page'),
    path('api/0.1/articles/', wiki_api.articles, name='wikiprox-api-articles'),
    re_path(r"^api/0.1/authors/(?P<url_title>[\w\W]+)/$", wiki_api.author, name='wikiprox-api-author'),
    path('api/0.1/authors/', wiki_api.authors, name='wikiprox-api-authors'),
    re_path(r'^api/0.1/categories/(?P<category>[\w]+)/$', wiki_api.category, name='wikiprox-api-category'),
    path('api/0.1/categories/', wiki_api.categories, name='wikiprox-api-categories'),
    path('api/0.1/events/', events_api.events, name='events-api-events'),
    re_path(r'^api/0.1/locations/(?P<category>[\w]+)/$', locations_api.category, name='locations-api-category'),
    path('api/0.1/locations/', locations_api.locations, name='locations-api-locations'),
    re_path(r"^api/0.1/sources/(?P<encyclopedia_id>[\w .:_-]+)/$", wiki_api.source, name='wikiprox-api-source'),
    path('api/0.1/sources/', wiki_api.sources, name='wikiprox-api-sources'),
    path('api/0.1/', front_api.index, name='front-api-index'),
    
    path('crossdomain.xml', TemplateView.as_view(template_name='crossdomain.xml')),
    path('qr/', TemplateView.as_view(template_name='front/qr.html'), name='qr'),
    path('robots.txt', TemplateView.as_view(template_name='front/robots.txt')),
    path('sitemap.xml', sitemap_views.sitemap, {'sitemaps': sitemaps}),
    #
    path('videotest/', TemplateView.as_view(template_name='wikiprox/LVplusJWPlayer.html')),
    #
    path('about/editorsmessage/embed/', TemplateView.as_view(template_name='front/editorsmessage-lightbox.html'), name='editorsmessageembed'),
    path('about/editorsmessage/', TemplateView.as_view(template_name='front/editorsmessage.html'), name='editorsmessage'),
    path('about/', TemplateView.as_view(template_name='front/about.html'), name='about'),
    path('history/', TemplateView.as_view(template_name='front/history.html')),
    path('search/', TemplateView.as_view(template_name='front/search.html')),
    path('terminology/', TemplateView.as_view(template_name='front/terminology.html')),
    #
    path('timeline/', events_views.events, name='events-events'),
    #
    re_path(r'^locations-(?P<category>[\w]+).kml$', locations_views.locations_kml, name='locations-kml-category'),
    path('locations.kml', locations_views.locations_kml, name='locations-kml'),
    re_path(r'^map/(?P<category>[\w]+)/$', locations_views.locations, name='locations-category'),
    path('map/', locations_views.locations, name='locations-index'),
    #
    # temp cite functionality patch 2013-03-26 gf
    path('citehelp/', TemplateView.as_view(template_name='front/citehelp.html'), name='citehelp'),
    #
    path('authors/', wiki_views.authors, name='wikiprox-authors'),
    path('categories/', wiki_views.categories, name='wikiprox-categories'),
    path('contents/', wiki_views.contents, name='wikiprox-contents'),
    re_path(r"^authors/(?P<url_title>[\w\W]+)/$", wiki_views.author, name='wikiprox-author'),
    re_path(r"^cite/source/(?P<encyclopedia_id>[\w .:_-]+)/$", wiki_views.source_cite, name='wikiprox-source-cite'),
    re_path(r"^sources/(?P<encyclopedia_id>[\w .:_-]+)/$", wiki_views.source, name='wikiprox-source'),
    re_path(r"^cite/page/(?P<url_title>[\w\W]+)/$", wiki_views.page_cite, name='wikiprox-page-cite'),
    re_path(r"^ddr/(?P<url_title>[\w\W]+)/$", wiki_views.related_ddr, name='wikiprox-related-ddr'),
    re_path(r"^print/(?P<url_title>[\w\W]+)/$", wiki_views.article, {'printed':True}, name='wikiprox-page-print'),
    re_path(r"^wiki/(?P<url_title>[\w\W]+)/$", wiki_views.wiki_article, name='wikiprox-wiki-page'),
    re_path(r"^(?P<url_title>[\w\W]+)/$", wiki_views.article, name='wikiprox-page'),
    # TODO fix this hack find the right way to deal with missing trailing slashes
    re_path(r"^(?P<url_title>[\w\W]+)$", wiki_views.article, name='wikiprox-page'),
    #
    path('', wiki_views.index, name='wikiprox-index'),
]
