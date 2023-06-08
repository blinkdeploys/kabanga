import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from __poll.constants import StatusChoices
from account.models import User
from __geo.factories import NationFactory, NationFactory
from __geo.models import Region
from __geo.serializers import NationSerializer


class RegionListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)        # Create some test regions
        self.nation = NationFactory()
        Region.objects.create(title='Region 1', nation=self.nation)
        Region.objects.create(title='Region 2', nation=self.nation)
        self.url = reverse('api_region_list')
    
    def test_region_list_get_unaunthenticated(self):
        response = self.client.get(self.url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_region_list_get(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url, format='json', content_type='application/json', HTTP_ACCEPT='application/json')
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data['data']), 2)


class RegionPostViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.nation = NationFactory()
        self.region = Region.objects.create(title='Region 1', nation=self.nation)
        self.url = reverse('api_region_post')

    def test_region_post_unauthorized(self):
        data = json.dumps({
                        'title': 'New Region',
                        'nation': NationSerializer(self.nation).data,
                        })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_region_post_invalid(self):
        self.client.login(username='testuser', password='testpassword')
        data = json.dumps({
                          'title': '',  # Invalid: Missing title
                          'nation': NationSerializer(self.nation).data,
                          'status': 'Active',
                        })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')  # Add format and HTTP_ACCEPT
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_region_post(self):
        self.client.login(username='testuser', password='testpassword')
        data = json.dumps({
                        'title': 'Updated Region',
                        'nation': NationSerializer(self.nation).data,
                        'status': 'Active',
                        })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.data
        self.assertEqual(response_data['title'], 'Updated Region')
        self.assertEqual(response_data['nation']['pk'], self.nation.pk)


class RegionDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.nation = NationFactory()
        self.region = Region.objects.create(title='Region 1', nation=self.nation)
        self.endpoint_alias = 'api_region_detail'

    def test_region_detail_get_unauthorized(self):
        url = reverse(self.endpoint_alias, args=[self.region.pk])
        response = self.client.get(url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_region_detail_put_unauthorized(self):
        url = reverse(self.endpoint_alias, args=[self.region.pk])
        data = json.dumps({
                'title': 'Updated Region',
                'nation': self.nation.pk,
                })
        response = self.client.put(url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_region_detail_delete_unauthorized(self):
        url = reverse(self.endpoint_alias, args=[self.region.pk])
        response = self.client.delete(url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_region_detail_get(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.region.pk])
        response = self.client.get(url, content_type='application/json', HTTP_ACCEPT='application/json')
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['title'], 'Region 1')
        self.assertEqual(response_data['nation']['pk'], self.nation.pk)

    def test_region_detail_put_invalid_data(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.region.pk])
        data = json.dumps({
                          'title': '',  # Invalid: Missing title
                          'nation': NationSerializer(self.nation).data,
                          'status': StatusChoices.ACTIVE,
                         })
        response = self.client.put(url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_region_detail_put(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.region.pk])
        data = json.dumps({
                          'title': 'Updated Region',
                          'nation': NationSerializer(self.nation).data,
                          'status': StatusChoices.ACTIVE,
                         })
        response = self.client.put(url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.region.refresh_from_db()
        self.assertEqual(self.region.title, 'Updated Region')

    def test_region_detail_delete(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.region.pk])
        response = self.client.delete(url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Region.objects.filter(pk=self.region.pk).exists())
