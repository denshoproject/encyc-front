from django.test import TestCase
from django.test.client import Client


def get_status(url):
    return Client().get(url).status_code

class WikiPageTitles(TestCase):
    """Test that characters in MediaWiki titles are matched correctly
    """
    def test_wiki_titles_space(self):
        self.assertEqual(200, get_status('/Ansel%20Adams/'))
    def test_wiki_titles_period(self):
        self.assertEqual(200, get_status('/A.L. Wirin/'))
    def test_wiki_titles_hyphen(self):
        self.assertEqual(200, get_status('/Aiko Herzig-Yoshinaga/'))
    def test_wiki_titles_parens(self):
        self.assertEqual(200, get_status('/Amache (Granada)/'))
    def twiki_titleshars_comma(self):
        self.assertEqual(200, get_status('/December 7, 1941/'))
    def test_wiki_titles_singlequote(self):
        self.assertEqual(200, get_status("/Hawai'i/"))
    def test_wiki_titles_slash(self):
        self.assertEqual(200, get_status('/Informants%20/%20"inu"/'))



import datetime
import json
import os

from bs4 import BeautifulSoup, SoupStrainer, Comment

from wikiprox import mediawiki as mw
from wikiprox import sample_data

class MediaWikiFunctions(TestCase):
    """Test various MediaWiki functions.
    """
    pagedata = sample_data.pagedata_Amache_20120829
    soup = BeautifulSoup(pagedata['parse']['text']['*'].replace('<p><br />\n</p>',''), 'html.parser')

    def test_page_is_published(self):
        self.assertEqual(True, mw.page_is_published(self.pagedata))
        
    def test_page_lastmod(self):
        lastmod = mw.page_lastmod('Encyclopedia')
        self.assertIsNotNone(lastmod)
        self.assertEqual(type(lastmod), type(datetime.datetime.now()))

    def test_remove_staticpage_titles(self):
        soup = mw.remove_staticpage_titles(self.soup)
        html = str(soup)
        self.assertEqual(-1, html.find('<h1>'))

    def test_remove_edit_links(self):
        soup = mw.remove_edit_links(self.soup)
        html = str(soup)
        self.assertEqual(-1, html.find('editsection'))
    
    def test_wrap_sections(self):
        pass

    def test_remove_status_markers(self):
        soup = mw.remove_status_markers(self.soup)
        html = str(soup)
        self.assertEqual(-1, html.find('class="alert'))

    def test_rewrite_mediawiki_urls(self):
        soup = mw.rewrite_mediawiki_urls(self.soup)
        html = str(soup)
        self.assertEqual(-1, html.find('/mediawiki/index.php'))

    def test_rewrite_newpage_links(self):
        soup = mw.rewrite_newpage_links(self.soup)
        html = str(soup)
        self.assertEqual(-1, html.find('&action=edit'))
        self.assertEqual(-1, html.find('&redlink=1'))
    
    def test_rewrite_prevnext_links(self):
        pass
    
    def test_extract_encyclopedia_id(self):
        pass
    
    def test_find_primary_sources(self):
        pass
    
    def test_remove_primary_sources(self):
        images = self.pagedata['parse']['images']
        primary_sources = mw.find_primary_sources(images)
        soup = mw.remove_primary_sources(self.soup, primary_sources)
        html = str(soup)
        self.assertEqual(-1, html.find('class="image"'))
    
    def test_find_databoxcamps_coordinates(self):
        coordinates = mw.find_databoxcamps_coordinates(self.pagedata['parse']['text']['*'])
        self.assertEqual((-102.3000,38.0500), coordinates)
    
    def test_add_top_links(self):
        pass
