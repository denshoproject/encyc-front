from django.test import TestCase
from django.urls import reverse


class APIView(TestCase):

    def test_index(self):
        assert self.client.get(reverse('front-api-index')).status_code == 200

    def test_locations(self):
        response = self.client.get(reverse('locations-api-locations'))
        assert response.status_code == 200
        assert 'Temporary Assembly Center' in response.content

    def test_locationscategory(self):
        response = self.client.get(
            reverse('locations-api-category', args=['tac'])
        )
        assert response.status_code == 200
        assert 'Temporary Assembly Center' in response.content


class TimelineTests(TestCase):
    
    def test_firstdate(self):
        response = self.client.get(reverse('locations-index'))
        assert 'Fresno, California' in response.content
