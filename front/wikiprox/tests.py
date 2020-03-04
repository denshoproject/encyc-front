from django.test import TestCase
from django.urls import reverse


class APIView(TestCase):

    def test_index(self):
        assert self.client.get(reverse('front-api-index')).status_code == 200

    def test_articles(self):
        data = {}
        response = self.client.get(reverse('wikiprox-api-articles'), data)
        assert response.status_code == 200
        data = {'offset': 25}
        response = self.client.get(reverse('wikiprox-api-articles'), data)
        assert response.status_code == 200

    def test_article(self):
        assert self.client.get(
            reverse('wikiprox-api-page', args=['Ansel Adams'])
        ).status_code == 200

    def test_authors(self):
        data = {}
        response = self.client.get(reverse('wikiprox-api-authors'), data)
        assert response.status_code == 200
        data = {'offset': 25}
        response = self.client.get(reverse('wikiprox-api-authors'), data)
        assert response.status_code == 200

    def test_author(self):
        assert self.client.get(
            reverse('wikiprox-api-author', args=['Kaori Akiyama'])
        ).status_code == 200


class WikiPageTitles(TestCase):
    """Test that characters in MediaWiki titles are matched correctly
    """
    
    def test_wiki_titles_space(self):
        assert self.client.get(
            reverse('wikiprox-page', args=['Ansel Adams'])
        ).status_code == 200
    
    #def test_wiki_titles_period(self):
    #    assert self.client.get('/A.L.%20Wirin/').status_code == 200
    
    def test_wiki_titles_hyphen(self):
        assert self.client.get(
            reverse('wikiprox-page', args=['Aiko Herzig-Yoshinaga'])
        ).status_code == 200
    
    #def test_wiki_titles_parens(self):
    #    assert self.client.get('/Amache%20(Granada)/').status_code == 200
    
    def twiki_titleshars_comma(self):
        assert self.client.get(
            reverse('wikiprox-page', args=['December 7, 1941'])
        ).status_code == 200
    
    #def test_wiki_titles_singlequote(self):
    #    assert self.client.get("/Hawai'i/").status_code == 200
    
    def test_wiki_titles_slash(self):
        assert self.client.get(
            reverse('wikiprox-page', args=['Informants / "inu"'])
        ).status_code == 200
