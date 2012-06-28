from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

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
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    #
    url(r'^videotest/$', direct_to_template, {'template': 'wikiprox/LVplusJWPlayer.html'}),
    #
    url(r'^search/$', direct_to_template, {'template': 'search.html'}),
    url(r"^contents/$", 'wikiprox.views.contents', name='wikiprox-contents'),
    url(r"^categories/$", 'wikiprox.views.categories', name='wikiprox-categories'),
    #
    url(r"^sources/(?P<encyclopedia_id>[\w .:_-]+)/$", 'wikiprox.views.source', name='wikiprox-source'),
    #
    url(r"^cite/source/(?P<encyclopedia_id>[\w .:_-]+)/$", 'wikiprox.views.source_cite', name='wikiprox-source-cite'),
    url(r"^cite/page/(?P<page>[\w\W]+)/$", 'wikiprox.views.page_cite', name='wikiprox-page-cite'),
    #
    url(r"^print/(?P<page>[\w\W]+)/$", 'wikiprox.views.page', {'printer':True}, name='wikiprox-page-print'),
    url(r"^([\w\W]+)/$", 'wikiprox.views.page', name='wikiprox-page'),
    url(r"^$", 'wikiprox.views.index', name='wikiprox-index'),
)
