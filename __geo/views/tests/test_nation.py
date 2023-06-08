from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from rest_framework.utils.serializer_helpers import ReturnList
from __poll.constants import FormMessages
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AnonymousUser

from account.models import User
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from __geo.factories import NationFactory
from __geo.views import nation_list
from __geo.views import nation_detail
from __geo.models import Nation
from __geo.forms import NationForm

'''
class NationListViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        nation = NationFactory()

    def test_unauthorized_access(self):
        # Create an unauthenticated request
        request = self.factory.get(reverse('nation_list'))
        request.user = AnonymousUser()
        response = nation_list(request)
        expected_redirect_url = '/accounts/login/'
        # Assert that the response is a redirect to the login page
        self.assertEqual(response.status_code, 302)
        self.assertIn(expected_redirect_url, response.url)

    def test_authorized_access(self):
        client = Client()
        client.login(username='testuser', password='testpassword')
        response = client.get(reverse('nation_list'), dict(user=self.user))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/nation_list.html')
        # Assert the context data
        context = response.context
        self.assertEqual(context['title'], 'Nations')
        self.assertEqual(len(context['data']), 1)
        self.assertEqual(context['count'], 1)
        self.assertEqual(len(context['columns']), 6)
        self.assertEqual(context['numpages'], 1)
        self.assertEqual(context['next_link'], '/geo/nations/?page=1')
        self.assertEqual(context['prev_link'], '/geo/nations/?page=1')
        # Additional assertions for pagination
        self.assertIsInstance(context['data'], ReturnList)
        # Additional assertions for query parameters
        self.assertEqual(context['request'].GET.get('q', ''), '')
        # self.assertEqual(context['request'].user, self.user)

    def test_empty_q_parameter(self):
        client = Client()
        client.login(username='testuser', password='testpassword')
        response = client.get(reverse('nation_list'), dict(q='', user=self.user))
        context = response.context
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(context['data']), 1)

    def test_non_empty_q_parameter(self):
        client = Client()
        client.login(username='testuser', password='testpassword')
        response = client.get(reverse('nation_list'), {'q': 'nation'})
        context = response.context
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(context['data']), 1)

    def test_not_found_q_parameter(self):
        client = Client()
        client.login(username='testuser', password='testpassword')
        response = client.get(reverse('nation_list'), {'q': 'region'})
        context = response.context
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(context['data']), 0)

    def test_page_parameter(self):
        client = Client()
        client.login(username='testuser', password='testpassword')
        response = client.get(reverse('nation_list'), {'page': 1})
        context = response.context
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(context['data']), 1)
'''


class NationListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_nation_list_unauthenticated(self):
        nation = Nation.objects.create(code='N', title='Test Nation 1')
        url = reverse('nation_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + url)

    def test_nation_list_view(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('nation_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/nation_list.html')
        self.assertEqual(response.context['title'], 'Nations')
        self.assertEqual(len(response.context['data']), 0)  # No nations initially
        self.assertEqual(response.context['count'], 0)
        self.assertEqual(response.context['numpages'], 1)
        self.assertEqual(response.context['next_link'], '/geo/nations/?page=1')
        self.assertEqual(response.context['prev_link'], '/geo/nations/?page=1')

    def test_nation_list_view_has_data(self):
        nation = Nation.objects.create(code='N1', title='Test Nation 1')
        self.client.login(username='testuser', password='testpassword')
        url = reverse('nation_list')
        response = self.client.get(url)
        self.assertEqual(len(response.context['data']), 1)
        with self.assertRaises(ValidationError):
            nation = Nation.objects.create(code='N2', title='Test Nation 2')


class NationDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.nation = Nation.objects.create(code='US', title='United States')

    def test_nation_detail_loads_on_get_method(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('nation_detail', kwargs={'pk': self.nation.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/nation_form.html')
        self.assertContains(response, 'Nation')
        self.assertContains(response, 'Save')
        self.assertIsInstance(response.context['elements'], NationForm)
        self.assertEqual(response.context['elements'].initial['pk'], self.nation.pk)
        self.assertEqual(response.context['elements'].initial['code'], self.nation.code)
        self.assertEqual(response.context['elements'].initial['title'], self.nation.title)

    def test_nation_detail_view_with_invalid_data(self):
        self.client.login(username='testuser', password='testpassword')

        url = reverse('nation_detail', kwargs={'pk': self.nation.pk})
        data = dict(code='US', title='')
        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/nation_form.html')
        self.assertContains(response, 'Nation')
        self.assertContains(response, 'Save')
        context = response.context
        self.assertEqual(int(context['pk']), self.nation.pk)
        self.assertIsInstance(context['elements'], NationForm)
        self.assertEqual(context['title'], 'Nation')
        self.assertEqual(context['detail_path'], 'nation_detail')
        self.assertEqual(context['list_path'], 'nation_list')
        self.assertEqual(context['message'], FormMessages.INVALID_FORM)

    def test_nation_detail_view_valid_data(self):
        self.client.login(username='testuser', password='testpassword')
        context = dict(pk=self.nation.pk)
        url = reverse('nation_detail', kwargs=context)
        data = dict(code='GH', title='Republic of Ghana')
        response = self.client.post(url, data, follow=True)
        self.nation.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('nation_detail', kwargs=context))
        self.assertEqual(self.nation.code, 'GH')
        self.assertEqual(self.nation.title, 'Republic of Ghana')
