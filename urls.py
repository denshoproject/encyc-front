from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns(
    '',
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^about/$', direct_to_template, {'template': 'about.html'}, name='about'),
    url(r'^search/$', direct_to_template, {'template': 'search.html'}, name='search'),
    url(r'^wiki/', include('wikiprox.urls')),
    url(r'^$', direct_to_template, {'template': 'index.html'}, name='index'),
)
