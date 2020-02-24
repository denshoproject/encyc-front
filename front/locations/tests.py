from django.test import TestCase
from django.urls import reverse


class TimelineTests(TestCase):
    
    def test_firstdate(self):
        response = self.client.get(reverse('locations-index'))
        assert 'Fresno, California' in response.content
