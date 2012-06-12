from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

#from django.contrib import admin
#admin.autodiscover()

from wikiprox.sitemaps import MediaWikiSitemap
sitemaps = {
    'wiki': MediaWikiSitemap,
}

urlpatterns = patterns(
    '',
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url(r'^about/$', direct_to_template, {'template': 'about.html'}, name='about'),
    url(r'^search/$', direct_to_template, {'template': 'search.html'}, name='search'),
    url(r'^wiki/', include('wikiprox.urls')),
    url(r'^$', direct_to_template, {'template': 'index.html'}, name='index'),
)
