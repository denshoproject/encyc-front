from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import path, re_path

from wikiprox import views

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS}, name='wikiprox-sitemap'),
    re_path(r"^index.php/(?P<page>[\w\W]+)/$", views.page, name='wikiprox-page'),
    re_path(r"^(?P<page>[\w\W]+)/$", views.page, name='wikiprox-page'),
    #
    path('', lambda x: HttpResponseRedirect('/wiki/%s' % settings.MEDIAWIKI_DEFAULT_PAGE)),
]

# problematic page titles
# period, comma, hyphen, parentheses, slash, single-quote/apostrophe
# Examples:
#   A.L. Wirin
#   Aiko Herzig-Yoshinaga
#   Amache (Granada)
#   Bureau of Sociological Research, Poston
#   Documentary films/videos on incarceration
#   Hawai'i
