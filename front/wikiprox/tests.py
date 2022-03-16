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
            reverse('wikiprox-api-author', args=['Brian Niiya'])
        ).status_code == 200

    #def test_sources(self):
    #    # can't browse sources independent of articles
    #    data = {}
    #    response = self.client.get(reverse('wikiprox-api-sources'), data)
    #    assert response.status_code == 200
    #    data = {'offset': 25}
    #    response = self.client.get(reverse('wikiprox-api-sources'), data)
    #    assert response.status_code == 200

    def test_source(self):
        assert self.client.get(
            reverse('wikiprox-api-source', args=['en-littletokyousa-1'])
        ).status_code == 200


class WikiPageTitles(TestCase):
    """Test that characters in MediaWiki titles are matched correctly
    """

    def test_titles_az(self):
        response = self.client.get(reverse('wikiprox-contents'))
        assert response.status_code == 200
        content = str(response.content)
        assert '<h2>1-10</h2>' in content
        assert '<a href="/1399th%20Engineer%20Construction%20Battalion">' in content
        assert '<h2>A</h2>' in content
        assert '<a href="/Ruth%20Asawa">Ruth Asawa</a>' in content
        assert '<h2>C</h2>' in content
        assert '<a href="/Chicago%20Brethren%20Hostel">' in content
        assert '<h2>D</h2>' in content
        assert '<a href="/Iva%20Toguri%20D&#x27;Aquino">' in content
        assert '<h2>N</h2>' in content
        assert '<a href="/Nisei%20Progressives">' in content
        assert '<h2>P</h2>' in content
        assert '<a href="/Pinedale%20(detention%20facility)">' in content
        assert '<h2>Z</h2>' in content
        assert '<a href="/Kenichi%20Zenimura">' in content

    def test_topics(self):
        response = self.client.get(reverse('wikiprox-categories'))
        assert response.status_code == 200
        content = str(response.content)
        assert '<h2>Arts</h2>' in content
        assert '<a href="/Ruth%20Asawa">Ruth Asawa</a>' in content
        assert '<h2>Camps</h2>' in content
        assert '<a href="/Pinedale%20(detention%20facility)">' in content
        assert '<h2>Organizations</h2>' in content
        assert '<a href="/Nisei%20Progressives">' in content
        assert '<h2>People</h2>' in content
        assert '<a href="/Iva%20Toguri%20D&#x27;Aquino">' in content
        assert '<h2>Resettlement</h2>' in content
        assert '<a href="/Chicago%20Brethren%20Hostel">' in content
    
    def test_wiki_titles_space(self):
        assert self.client.get(
            reverse('wikiprox-page', args=['Ansel Adams'])
        ).status_code == 200
    
    def test_wiki_titles_period(self):
        assert self.client.get('/A.L.%20Wirin/').status_code == 200
    
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
    
    def test_authors(self):
        response = self.client.get(reverse('wikiprox-authors'))
        assert response.status_code == 200
        content = str(response.content)
        assert 'span3 column1' in content
        assert '/authors/Brian%20Niiya/' in content
        assert 'Brian Niiya' in content
    
    def test_author(self):
        response = self.client.get(
            reverse('wikiprox-author', args=['Brian Niiya'])
        )
        assert response.status_code == 200
        content = str(response.content)
        assert 'Brian Niiya' in content
        assert 'is the content director' in content
        assert '<a href="/A.L.%20Wirin/">A.L. Wirin</a>' in content
