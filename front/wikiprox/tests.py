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
