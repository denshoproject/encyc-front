from django.test import TestCase
from django.urls import reverse


class WikiPageTitles(TestCase):
    """Test that characters in MediaWiki titles are matched correctly
    """
    
    def test_wiki_titles_space(self):
        assert self.client.get(
            reverse('wikiprox-page', args=['Ansel%20Adams'])
        ).status_code == 200
    
    #def test_wiki_titles_period(self):
    #    assert self.client.get('/A.L.%20Wirin/').status_code == 200
    
    def test_wiki_titles_hyphen(self):
        assert self.client.get('/Aiko%20Herzig-Yoshinaga/').status_code == 200
    
    #def test_wiki_titles_parens(self):
    #    assert self.client.get('/Amache%20(Granada)/').status_code == 200
    
    def twiki_titleshars_comma(self):
        assert self.client.get('/December%207,%201941December 7, 1941/').status_code == 200
    
    #def test_wiki_titles_singlequote(self):
    #    assert self.client.get("/Hawai'i/").status_code == 200
    
    def test_wiki_titles_slash(self):
        assert self.client.get('/Informants%20/%20"inu"/').status_code == 200
