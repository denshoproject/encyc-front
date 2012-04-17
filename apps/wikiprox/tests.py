from django.test import TestCase
from django.test.client import Client


MW_URL = '/mediawiki/index.php/%s/'

def get_response(url):
    c = Client()
    return c.get(url)
def get_status(url):
    return get_response(url).status_code


class WikiPageTitles(TestCase):
    """Test that characters in MediaWiki titles are matched correctly
    """
    def test_wiki_titles_space(self):
        self.assertEqual(200, get_status(MW_URL % 'Ansel Adams'))
    def test_wiki_titles_period(self):
        self.assertEqual(200, get_status(MW_URL % 'A.L. Wirin'))
    def test_wiki_titles_hyphen(self):
        self.assertEqual(200, get_status(MW_URL % 'Aiko Herzig-Yoshinaga'))
    def test_wiki_titles_parens(self):
        self.assertEqual(200, get_status(MW_URL % 'Amache (Granada)'))
    def twiki_titleshars_comma(self):
        self.assertEqual(200, get_status(MW_URL % 'December 7, 1941'))
    def test_wiki_titles_singlequote(self):
        self.assertEqual(200, get_status(MW_URL % "Hawai'i"))
    def test_wiki_titles_slash(self):
        self.assertEqual(200, get_status(MW_URL % 'Informants / inu'))
