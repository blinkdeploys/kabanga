import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from __poll.constants import StatusChoices
from account.models import User
from __geo.factories import NationFactory, RegionFactory
from __geo.models import Constituency
from __geo.serializers import RegionSerializer


class ConstituencyListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)        # Create some test constituencys
        nation = NationFactory()
        self.region = RegionFactory(nation=nation)
        Constituency.objects.create(title='Constituency 1', region=self.region)
        Constituency.objects.create(title='Constituency 2', region=self.region)
        self.url = reverse('api_constituency_list')
    
    def test_constituency_list_get_unaunthenticated(self):
        response = self.client.get(self.url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_constituency_list_get(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url, format='json', content_type='application/json', HTTP_ACCEPT='application/json')
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data['data']), 2)


class ConstituencyPostViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        nation = NationFactory()
        self.region = RegionFactory(nation=nation)
        self.constituency = Constituency.objects.create(title='Constituency 1', region=self.region)
        self.url = reverse('api_constituency_post')

    def test_constituency_post_unauthorized(self):
        data = json.dumps({
                        'title': 'New Constituency',
                        'region': RegionSerializer(self.region).data,
                        })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_constituency_post_invalid(self):
        self.client.login(username='testuser', password='testpassword')
        data = json.dumps({
                          'title': '',  # Invalid: Missing title
                          'region': RegionSerializer(self.region).data,
                          'status': 'Active',
                        })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')  # Add format and HTTP_ACCEPT
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_constituency_post(self):
        self.client.login(username='testuser', password='testpassword')
        data = json.dumps({
                        'title': 'Updated Constituency',
                        'region': RegionSerializer(self.region).data,
                        'status': 'Active',
                        })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.data
        self.assertEqual(response_data['title'], 'Updated Constituency')
        self.assertEqual(response_data['region']['pk'], self.region.pk)


class ConstituencyDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        nation = NationFactory()
        self.region = RegionFactory(nation=nation)
        self.constituency = Constituency.objects.create(title='Constituency 1', region=self.region)
        self.endpoint_alias = 'api_constituency_detail'

    def test_constituency_detail_get_unauthorized(self):
        url = reverse(self.endpoint_alias, args=[self.constituency.pk])
        response = self.client.get(url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_constituency_detail_put_unauthorized(self):
        url = reverse(self.endpoint_alias, args=[self.constituency.pk])
        data = json.dumps({
                'title': 'Updated Constituency',
                'region': self.region.pk,
                })
        response = self.client.put(url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_constituency_detail_delete_unauthorized(self):
        url = reverse(self.endpoint_alias, args=[self.constituency.pk])
        response = self.client.delete(url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_constituency_detail_get(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.constituency.pk])
        response = self.client.get(url, content_type='application/json', HTTP_ACCEPT='application/json')
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['title'], 'Constituency 1')
        self.assertEqual(response_data['region']['pk'], self.region.pk)

    def test_constituency_detail_put_invalid_data(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.constituency.pk])
        data = json.dumps({
                          'title': '',  # Invalid: Missing title
                          'region': RegionSerializer(self.region).data,
                          'status': StatusChoices.ACTIVE,
                         })
        response = self.client.put(url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_constituency_detail_put(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.constituency.pk])
        data = json.dumps({
                          'title': 'Updated Constituency',
                          'region': RegionSerializer(self.region).data,
                          'status': StatusChoices.ACTIVE,
                         })
        response = self.client.put(url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.constituency.refresh_from_db()
        self.assertEqual(self.constituency.title, 'Updated Constituency')

    def test_constituency_detail_delete(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.constituency.pk])
        response = self.client.delete(url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Constituency.objects.filter(pk=self.constituency.pk).exists())
