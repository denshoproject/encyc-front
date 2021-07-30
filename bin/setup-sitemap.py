# encyc-front sitemap setup
# In order for sitemaps.xml to show the correct domain name,
# django.contrib.sitemaps requires django.contrib.sites and
# requires the proper domain name for Site 1.

from django.contrib.sites.models import Site

s = Site.objects.get(id=1)
s.name = "Densho Encyclopedia"
s.domain = 'encyclopedia.densho.org'
s.save()
