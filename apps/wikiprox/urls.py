from django.conf.urls.defaults import *

from wikiprox import views

urlpatterns = patterns(
    '',
    # files (tansu)
    url(r'^index.php/File:([\w .:_-]+)/$', views.media, name='wikiprox-media'),
    url(r'^File:([\w .:_-]+)/$', views.media, name='wikiprox-media'),
    # pages (mediawiki)
    url(r'^index.php/([\w .:_-]+)/$', views.page, name='wikiprox-page'),
    url(r'^([\w .:_-]+)/$', views.page, name='wikiprox-page'),
    #
    url(r'^$', views.index, name='wikiprox-index'),
)
