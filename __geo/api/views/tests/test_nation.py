import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from __poll.constants import StatusChoices
from account.models import User
from __geo.factories import NationFactory, NationFactory
from __geo.models import Nation
from __geo.serializers import NationSerializer
from django.core.exceptions import ValidationError


class NationListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)        # Create some test nations
        self.nation = NationFactory(title='Nation 1')
        self.url = reverse('api_nation_list')
    
    def test_nation_list_get_unaunthenticated(self):
        response = self.client.get(self.url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_nation_list_get(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url, format='json', content_type='application/json', HTTP_ACCEPT='application/json')  # Add format and HTTP_ACCEPT
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data['data']), 1)


class NationPostViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('api_nation_post')

    def test_nation_post_unauthorized(self):
        self.nation = NationFactory(title='Nation 1')
        data = json.dumps({
                        'code': 'NN',
                        'title': 'New Nation',
                        })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_nation_post_invalid(self):
        self.client.login(username='testuser', password='testpassword')
        data = json.dumps({
                          'code': '',
                          'title': '',
                        })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')  # Add format and HTTP_ACCEPT
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nation_post_again_throws_exception(self):
        self.client.login(username='testuser', password='testpassword')
        self.nation = NationFactory(title='Nation 1')
        data = json.dumps({
                        'code': 'N1',
                        'title': 'Updated Nation',
                        })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nation_post(self):
        self.client.login(username='testuser', password='testpassword')
        data = json.dumps({
                        'code': 'N1',
                        'title': 'New Nation',
                        })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data['code'], 'N1')
        self.assertEqual(response_data['title'], 'New Nation')


class NationDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.nation = NationFactory(code="N1", title="Nation 1")
        self.endpoint_alias = 'api_nation_detail'

    def test_nation_detail_get_unauthorized(self):
        url = reverse(self.endpoint_alias, args=[self.nation.pk])
        response = self.client.get(url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_nation_detail_put_unauthorized(self):
        url = reverse(self.endpoint_alias, args=[self.nation.pk])
        data = json.dumps({
                'code': 'UN',
                'title': 'Updated Nation',
                })
        response = self.client.put(url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_nation_detail_delete_unauthorized(self):
        url = reverse(self.endpoint_alias, args=[self.nation.pk])
        response = self.client.delete(url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_nation_detail_get(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.nation.pk])
        response = self.client.get(url, content_type='application/json', HTTP_ACCEPT='application/json')
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['code'], 'N1')
        self.assertEqual(response_data['title'], 'Nation 1')

    def test_nation_detail_put_invalid_data(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.nation.pk])
        data = json.dumps({
                          'code': '',
                          'title': '',
                         })
        response = self.client.put(url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nation_detail_put(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.nation.pk])
        data = json.dumps({
                          'code': 'UN',
                          'title': 'Updated Nation',
                         })
        response = self.client.put(url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.nation.refresh_from_db()
        self.assertEqual(self.nation.title, 'Updated Nation')

    def test_nation_detail_delete(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.nation.pk])
        response = self.client.delete(url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Nation.objects.filter(pk=self.nation.pk).exists())
