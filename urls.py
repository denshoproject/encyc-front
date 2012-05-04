from django.conf.urls.defaults import patterns, include, url
from django.http import HttpResponseRedirect

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns(
    '',
    #url(r'^mediawiki/', include('wikiprox.urls')),
    url(r'^wiki/', include('wikiprox.urls')),
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^$', lambda x: HttpResponseRedirect('/wiki/Main_Page')),
)
