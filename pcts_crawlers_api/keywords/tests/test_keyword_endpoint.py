from rest_framework.test import APITestCase
from django.urls import reverse
from datetime import datetime
import json
from keywords.models import Keyword

from django.contrib.auth import get_user_model


class KeywordEndpoint(APITestCase):
    def setUp(self):
        self.endpoint = '/api/keywords/'

        Keyword.objects.bulk_create([
            Keyword(keyword="quilombolas"),
            Keyword(keyword="povos e comunidades tradicionais"),
        ])

        self.keyword = {
            "keyword": "indígenas"
        }

    def tearDown(self):
        Keyword.objects.all().delete()

    def user_login(self):
        username = "admin"
        email = "admin@email.com"
        password = "admin"

        User = get_user_model()
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password)

        return json.loads(
            self.client.post(
                '/token/',
                {
                    "username": username,
                    "password": password
                }
            ).content)["access"]

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
        token = self.user_login()

        response = self.client.post(
            self.endpoint,
            self.keyword,
            HTTP_AUTHORIZATION='Bearer {}'.format(token)
        )

        json_response = json.loads(response.content)

        self.assertEqual(201, response.status_code)
        self.assertEqual(self.keyword['keyword'], json_response['keyword'])

    def test_get(self):
        token = self.user_login()

        # Keyword create
        keyword_response = json.loads(self.client.post(
            self.endpoint,
            self.keyword,
            HTTP_AUTHORIZATION='Bearer {}'.format(token)
        ).content)

        response = self.client.get(
            f"{self.endpoint}{keyword_response['id']}/",
            format='json'
        )

        json_response = json.loads(response.content)

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.keyword['keyword'], json_response['keyword'])

    def test_update(self):
        token = self.user_login()

        # Keyword create
        keyword_response = json.loads(self.client.post(
            self.endpoint,
            self.keyword,
            HTTP_AUTHORIZATION='Bearer {}'.format(token)
        ).content)

        keyword_update = {
            "keyword": "índio"
        }
        updated_response = self.client.put(
            f"{self.endpoint}{keyword_response['id']}/",
            keyword_update,
            HTTP_AUTHORIZATION='Bearer {}'.format(token)
        )

        json_response = json.loads(updated_response.content)

        self.assertEqual(200, updated_response.status_code)
        self.assertEqual(keyword_update['keyword'], json_response['keyword'])

    def test_delete(self):
        token = self.user_login()

        # Keyword create
        keyword_response = json.loads(self.client.post(
            self.endpoint,
            self.keyword,
            HTTP_AUTHORIZATION='Bearer {}'.format(token)
        ).content)

        response = self.client.delete(
            f"{self.endpoint}{keyword_response['id']}/",
            format='json',
            HTTP_AUTHORIZATION='Bearer {}'.format(token)
        )
        self.assertEqual(204, response.status_code)
