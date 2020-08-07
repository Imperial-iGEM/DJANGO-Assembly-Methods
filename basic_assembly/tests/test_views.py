from django.test import TestCase, Client
from django.urls import reverse, resolve
from basic_assembly.views import BasicView
from basic_assembly.models import BasicModel
import json

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()

    def test_project_list_GET(self):
        client = Client()

        response = client.get(reverse('Basic-list'))
        self.assertEquals(response.status_code, 200)