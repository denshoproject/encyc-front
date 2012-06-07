from django.conf.urls.defaults import *

from wikiprox import views

urlpatterns = patterns(
    '',
    # files (tansu)
    url(r"^index.php/File:([\w .:_-]+)/$", views.media, name='wikiprox-media'),
    url(r"^File:([\w .:_-]+)/$", views.source, name='wikiprox-source'),
    # pages (mediawiki)
    url(r"^index.php/([\w\W]+)/$", views.page, name='wikiprox-page'),
    url(r"^([\w\W]+)/$", views.page, name='wikiprox-page'),
    #
    url(r'^$', views.index, name='wikiprox-index'),
)

# problematic page titles
# period, comma, hyphen, parentheses, slash, single-quote/apostrophe
# Examples:
#   A.L. Wirin
#   Aiko Herzig-Yoshinaga
#   Amache (Granada)
#   Bureau of Sociological Research, Poston
#   Documentary films/videos on incarceration
#   Hawai'i
