from django.test import TestCase
from django.urls import reverse


class TimelineTests(TestCase):
    
    def test_firstdate(self):
        response = self.client.get(reverse('events-events'))
        assert 'March 26, 1790' in response.content
