from django.test import TestCase
from django.urls import reverse


class APIView(TestCase):

    def test_index(self):
        assert self.client.get(reverse('front-api-index')).status_code == 200

    def test_events(self):
        response = self.client.get(reverse('events-api-events'))
        assert response.status_code == 200
        assert 'President Roosevelt signs Executive Order 9066' in response.content


class TimelineTests(TestCase):
    
    def test_firstdate(self):
        response = self.client.get(reverse('events-events'))
        assert 'March 26, 1790' in response.content
