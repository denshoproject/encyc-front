from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib.sitemaps import views as sitemap_views

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
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^api/0.1/urls-titles/$', wiki_views.api_contents, name='wikiprox-api-contents'),
    url(r"^api/0.1/articles/(?P<url_title>[\w\W]+)/$", wiki_api.article, name='wikiprox-api-page'),
    url(r'^api/0.1/articles/$', wiki_api.articles, name='wikiprox-api-articles'),
    url(r"^api/0.1/authors/(?P<url_title>[\w\W]+)/$", wiki_api.author, name='wikiprox-api-author'),
    url(r'^api/0.1/authors/$', wiki_api.authors, name='wikiprox-api-authors'),
    url(r'^api/0.1/categories/(?P<category>[\w]+)/$', wiki_api.category, name='wikiprox-api-category'),
    url(r'^api/0.1/categories/$', wiki_api.categories, name='wikiprox-api-categories'),
    url(r'^api/0.1/events/$', events_api.events, name='events-api-events'),
    url(r'^api/0.1/locations/(?P<category>[\w]+)/$', locations_api.category, name='locations-api-category'),
    url(r'^api/0.1/locations/$', locations_api.locations, name='locations-api-locations'),
    url(r"^api/0.1/sources/(?P<encyclopedia_id>[\w .:_-]+)/$", wiki_api.source, name='wikiprox-api-source'),
    url(r"^api/0.1/sources/$", wiki_api.sources, name='wikiprox-api-sources'),
    url(r'^api/0.1/$', front_api.index, name='front-api-index'),
    
    url(r'^crossdomain\.xml$', TemplateView.as_view(template_name='crossdomain.xml')),
    url(r'^qr/$', TemplateView.as_view(template_name='front/qr.html'), name='qr'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='front/robots.txt')),
    url(r'^sitemap\.xml$', sitemap_views.sitemap, {'sitemaps': sitemaps}),
    #
    url(r'^videotest/$', TemplateView.as_view(template_name='wikiprox/LVplusJWPlayer.html')),
    #
    url(r'^about/editorsmessage/embed/$', TemplateView.as_view(template_name='front/editorsmessage-lightbox.html'), name='editorsmessageembed'),
    url(r'^about/editorsmessage/$', TemplateView.as_view(template_name='front/editorsmessage.html'), name='editorsmessage'),
    url(r'^about/$', TemplateView.as_view(template_name='front/about.html'), name='about'),
    url(r'^history/$', TemplateView.as_view(template_name='front/history.html')),
    url(r'^search/$', TemplateView.as_view(template_name='front/search.html')),
    url(r'^terminology/$', TemplateView.as_view(template_name='front/terminology.html')),
    #
    url(r'^timeline/$', events_views.events, name='events-events'),
    #
    url(r'^map/(?P<category>[\w]+)/$', locations_views.locations, name='locations-category'),
    url(r'^map/$', locations_views.locations, name='locations-index'),
    #
    # temp cite functionality patch 2013-03-26 gf
    url(r'^citehelp/$', TemplateView.as_view(template_name='front/citehelp.html'), name='citehelp'),
    #
    url(r'^authors/$', wiki_views.authors, name='wikiprox-authors'),
    url(r'^categories/$', wiki_views.categories, name='wikiprox-categories'),
    url(r'^contents/$', wiki_views.contents, name='wikiprox-contents'),
    url(r"^authors/(?P<url_title>[\w\W]+)/$", wiki_views.author, name='wikiprox-author'),
    url(r"^cite/source/(?P<encyclopedia_id>[\w .:_-]+)/$", wiki_views.source_cite, name='wikiprox-source-cite'),
    url(r"^sources/(?P<encyclopedia_id>[\w .:_-]+)/$", wiki_views.source, name='wikiprox-source'),
    url(r"^cite/page/(?P<url_title>[\w\W]+)/$", wiki_views.page_cite, name='wikiprox-page-cite'),
    url(r"^ddr/(?P<url_title>[\w\W]+)/$", wiki_views.related_ddr, name='wikiprox-related-ddr'),
    url(r"^print/(?P<url_title>[\w\W]+)/$", wiki_views.article, {'printed':True}, name='wikiprox-page-print'),
    url(r"^(?P<url_title>[\w\W]+)/$", wiki_views.article, name='wikiprox-page'),
    #
    url(r"^$", wiki_views.index, name='wikiprox-index'),
]
