from django.conf.urls.defaults import *

from wikiprox import views

urlpatterns = patterns(
    '',
    url(r'^index.php/(\w+)/$', views.page, name='wikiprox-page'),
    url(r'^$', views.index, name='wikiprox-index'),
)
