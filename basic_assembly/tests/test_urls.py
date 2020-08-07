from django.test import SimpleTestCase
from django.urls import reverse, resolve
from basic_assembly.views import BasicView

class TestUrls(SimpleTestCase):

    def test_basic_url_has_correct_route(self):
        url = reverse('Basic-list')
        self.assertEquals(resolve(url).route, '^Basic/$')

    def test_basic_url_has_correct_name(self):
        url = reverse('Basic-list')
        self.assertEquals(resolve(url).url_name, 'Basic-list')

    def test_basic_url_has_correct_args(self):
        url = reverse('Basic-list')
        self.assertEquals(resolve(url).args, ())

    def test_basic_url_has_correct_kwargs(self):
        url = reverse('Basic-list')
        self.assertEquals(resolve(url).kwargs, {})

    def test_basic_url_has_correct_app_names(self):
        url = reverse('Basic-list')
        self.assertEquals(resolve(url).app_names, [])

    def test_basic_url_has_correct_namespaces(self):
        url = reverse('Basic-list')
        self.assertEquals(resolve(url).namespaces, [])

    def test_basic_url_function(self):
        url = reverse('Basic-list')
        type1 = type(resolve(url).func)
        type2 = type(BasicView.as_view({'get': 'list'}))
        self.assertTrue(type1 == type2)