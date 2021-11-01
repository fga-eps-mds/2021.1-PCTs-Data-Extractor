from rest_framework.test import APITestCase
from django.urls import reverse
from datetime import datetime
import json
from keywords.models import Keyword


class KeywordEndpoint(APITestCase):
    def setUp(self):
        self.endpoint = '/api/keywords/'

        Keyword.objects.bulk_create([
            Keyword(keyword="quilombolas"),
            Keyword(keyword="povos e comunidades tradicionais"),
        ])
    
    def tearDown(self):
        Keyword.objects.all().delete()

    def test_list_all_crawlers(self):
        response = json.loads(self.client.get(
            self.endpoint,
            format='json'
        ).content)
        
        print(response)
        self.assertEqual(
            2,
            len(response['results']),
        )