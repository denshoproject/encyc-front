from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

#from django.contrib import admin
#admin.autodiscover()

from wikiprox.sitemaps import MediaWikiSitemap, SourceSitemap
sitemaps = {
    'wiki': MediaWikiSitemap,
    'sources': SourceSitemap,
}

urlpatterns = patterns(
    '',
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^api/0.1/urls-titles/$', 'wikiprox.views.api_contents', name='wikiprox-api-contents'),
    url(r"^api/0.1/articles/(?P<url_title>[\w\W]+)/$", 'wikiprox.api.article', name='wikiprox-api-page'),
    url(r'^api/0.1/articles/$', 'wikiprox.api.articles', name='wikiprox-api-articles'),
    url(r"^api/0.1/authors/(?P<url_title>[\w\W]+)/$", 'wikiprox.api.author', name='wikiprox-api-author'),
    url(r'^api/0.1/authors/$', 'wikiprox.api.authors', name='wikiprox-api-authors'),
    url(r'^api/0.1/categories/(?P<category>[\w]+)/$', 'wikiprox.api.category', name='wikiprox-api-category'),
    url(r'^api/0.1/categories/$', 'wikiprox.api.categories', name='wikiprox-api-categories'),
    url(r'^api/0.1/events/$', 'events.api.events', name='events-api-events'),
    url(r'^api/0.1/locations/(?P<category>[\w]+)/$', 'locations.api.category', name='locations-api-category'),
    url(r'^api/0.1/locations/$', 'locations.api.locations', name='locations-api-locations'),
    url(r"^api/0.1/sources/(?P<encyclopedia_id>[\w .:_-]+)/$", 'wikiprox.api.source', name='wikiprox-api-source'),
    url(r"^api/0.1/sources/$", 'wikiprox.api.sources', name='wikiprox-api-sources'),
    url(r'^api/0.1/$', 'front.api.index', name='front-api-index'),
    
    url(r'^crossdomain\.xml$', TemplateView.as_view(template_name='crossdomain.xml')),
    url(r'^qr/$', TemplateView.as_view(template_name='qr.html'), name='qr'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt')),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    #
    url(r'^videotest/$', TemplateView.as_view(template_name='wikiprox/LVplusJWPlayer.html')),
    #
    url(r'^about/editorsmessage/embed/$', TemplateView.as_view(template_name='editorsmessage-lightbox.html'), name='editorsmessageembed'),
    url(r'^about/editorsmessage/$', TemplateView.as_view(template_name='editorsmessage.html'), name='editorsmessage'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^history/$', TemplateView.as_view(template_name='history.html')),
    url(r'^search/$', TemplateView.as_view(template_name='search.html')),
    url(r'^terminology/$', TemplateView.as_view(template_name='terminology.html')),
    #
    url(r'^timeline/$', 'events.views.events', name='events-events'),
    #
    url(r'^locations-(?P<category>[\w]+).kml$', 'locations.views.locations_kml', name='locations-kml-category'),
    url(r'^locations.kml$', 'locations.views.locations_kml', name='locations-kml'),
    url(r'^map/(?P<category>[\w]+)/$', 'locations.views.locations', name='locations-category'),
    url(r'^map/$', 'locations.views.locations', name='locations-index'),
    #
    # temp cite functionality patch 2013-03-26 gf
    url(r'^citehelp/$', TemplateView.as_view(template_name='citehelp.html'), name='citehelp'),
    #
    url(r'^authors/$', 'wikiprox.views.authors', name='wikiprox-authors'),
    url(r'^categories/$', 'wikiprox.views.categories', name='wikiprox-categories'),
    url(r'^contents/$', 'wikiprox.views.contents', name='wikiprox-contents'),
    url(r"^authors/(?P<url_title>[\w\W]+)/$", 'wikiprox.views.author', name='wikiprox-author'),
    url(r"^cite/source/(?P<encyclopedia_id>[\w .:_-]+)/$", 'wikiprox.views.source_cite', name='wikiprox-source-cite'),
    url(r"^sources/(?P<encyclopedia_id>[\w .:_-]+)/$", 'wikiprox.views.source', name='wikiprox-source'),
    url(r"^cite/page/(?P<url_title>[\w\W]+)/$", 'wikiprox.views.page_cite', name='wikiprox-page-cite'),
    url(r"^ddr/(?P<url_title>[\w\W]+)/$", 'wikiprox.views.related_ddr', name='wikiprox-related-ddr'),
    url(r"^print/(?P<url_title>[\w\W]+)/$", 'wikiprox.views.article', {'printed':True}, name='wikiprox-page-print'),
    url(r"^(?P<url_title>[\w\W]+)/$", 'wikiprox.views.article', name='wikiprox-page'),
    #
    url(r"^$", 'wikiprox.views.index', name='wikiprox-index'),
)
