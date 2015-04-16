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
    url(r'^api/0.1/urls-titles/$', 'wikiprox.views.api_contents', name='wikiprox-api-contents'),
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
    url(r'^authors/$', 'wikiprox.views_es.authors', name='wikiprox-authors'),
    url(r'^categories/$', 'wikiprox.views_es.categories', name='wikiprox-categories'),
    url(r'^contents/$', 'wikiprox.views_es.contents', name='wikiprox-contents'),
    url(r"^authors/(?P<url_title>[\w\W]+)/$", 'wikiprox.views_es.author', name='wikiprox-author'),
    url(r"^cite/source/(?P<encyclopedia_id>[\w .:_-]+)/$", 'wikiprox.views_es.source_cite', name='wikiprox-source-cite'),
    url(r"^sources/(?P<encyclopedia_id>[\w .:_-]+)/$", 'wikiprox.views_es.source', name='wikiprox-source'),
    url(r"^cite/page/(?P<url_title>[\w\W]+)/$", 'wikiprox.views_es.page_cite', name='wikiprox-page-cite'),
    url(r"^ddr/(?P<url_title>[\w\W]+)/$", 'wikiprox.views_es.related_ddr', name='wikiprox-related-ddr'),
    url(r"^print/(?P<url_title>[\w\W]+)/$", 'wikiprox.views_es.article', {'printed':True}, name='wikiprox-page-print'),
    url(r"^(?P<url_title>[\w\W]+)/$", 'wikiprox.views_es.article', name='wikiprox-page'),
    #
    url(r"^$", 'wikiprox.views.index', name='wikiprox-index'),
)
