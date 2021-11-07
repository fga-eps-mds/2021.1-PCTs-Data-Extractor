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

        self.keyword = {
            "keyword":"indígenas"
        }
    
    def tearDown(self):
        Keyword.objects.all().delete()

    def test_list_all_keywords(self):
        response = json.loads(self.client.get(
            self.endpoint,
            format='json'
        ).content)
        
        self.assertEqual(
            2,
            len(response['results']),
        )
    
    def test_create(self):
        response = self.client.post(
            self.endpoint,
            self.keyword
        )

        json_response = json.loads(response.content)
        
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.keyword['keyword'], json_response['keyword'])

        return json_response['id']

    def test_get(self):
        keyword_id = self.test_create()

        response = self.client.get(
            f"{self.endpoint}{keyword_id}/",
            format='json'
        )

        json_response = json.loads(response.content)

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.keyword['keyword'], json_response['keyword'])

    def test_update(self):
        keyword_id = self.test_create()

        keyword_update = {
            "keyword":"índio"
        }
        updated_response = self.client.put(
            f"{self.endpoint}{keyword_id}/",
            keyword_update
        )

        json_response = json.loads(updated_response.content)

        self.assertEqual(200, updated_response.status_code)
        self.assertEqual(keyword_update['keyword'], json_response['keyword'])
        
    def test_delete(self):
        keyword_id = self.test_create()
        response = self.client.delete(
            f"{self.endpoint}{keyword_id}/",
            format='json'
        )
        self.assertEqual(204, response.status_code)