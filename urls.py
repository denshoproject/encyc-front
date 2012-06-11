from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.http import HttpResponseRedirect

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns(
    '',
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^wiki/', include('wikiprox.urls')),
    url(r'^$', lambda x: HttpResponseRedirect('/wiki/%s' % settings.WIKIPROX_MEDIAWIKI_DEFAULT_PAGE)),
)
