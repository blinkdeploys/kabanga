import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from __poll.constants import StatusChoices
from account.models import User
from __geo.factories import NationFactory, RegionFactory, ConstituencyFactory
from __geo.models import Station
from __geo.serializers import ConstituencySerializer



class StationListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)        # Create some test stations
        nation = NationFactory()
        region = RegionFactory(nation=nation)
        self.constituency = ConstituencyFactory(region=region)
        Station.objects.create(title='Station 1', code='ABC', constituency=self.constituency)
        Station.objects.create(title='Station 2', code='DEF', constituency=self.constituency)
        self.url = reverse('api_station_list')
    
    def test_station_list_get_unaunthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_station_list_get(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url, format='json', content_type='application/json', HTTP_ACCEPT='application/json')  # Add format and HTTP_ACCEPT
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data['data']), 2)


class StationPostViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        nation = NationFactory()
        region = RegionFactory(nation=nation)
        self.constituency = ConstituencyFactory(region=region)
        self.station = Station.objects.create(title='Station 1', code='ABC', constituency=self.constituency)
        self.url = reverse('api_station_post')

    def test_station_post_unauthorized(self):
        data = json.dumps({
                        'code': 'XYZ',
                        'title': 'New Station',
                        'constituency': ConstituencySerializer(self.constituency).data,
                        })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_station_post_invalid(self):
        self.client.login(username='testuser', password='testpassword')
        data = json.dumps({
                'code': 'XYZ',
                'title': '',  # Invalid: Missing title
                'constituency': ConstituencySerializer(self.constituency).data,
                'status': 'Active',
                })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')  # Add format and HTTP_ACCEPT
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_station_post(self):
        self.client.login(username='testuser', password='testpassword')
        data = json.dumps({
                        'code': 'UST',
                        'title': 'Updated Station',
                        'constituency': ConstituencySerializer(self.constituency).data,
                        'status': 'Active',
                        })
        response = self.client.post(self.url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.data
        self.assertEqual(response_data['code'], 'UST')
        self.assertEqual(response_data['title'], 'Updated Station')
        self.assertEqual(response_data['constituency']['pk'], self.constituency.pk)


class StationDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        nation = NationFactory()
        region = RegionFactory(nation=nation)
        self.constituency = ConstituencyFactory(region=region)
        self.station = Station.objects.create(title='Station 1', code='ABC', constituency=self.constituency)
        self.endpoint_alias = 'api_station_detail'

    def test_station_detail_get_unauthorized(self):
        url = reverse(self.endpoint_alias, args=[self.station.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_station_detail_put_unauthorized(self):
        url = reverse(self.endpoint_alias, args=[self.station.pk])
        data = {
            'code': 'XYZ',
            'title': 'Updated Station',
            'constituency': self.constituency.pk,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_station_detail_delete_unauthorized(self):
        url = reverse(self.endpoint_alias, args=[self.station.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_station_detail_get(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.station.pk])
        response = self.client.get(url, content_type='application/json', HTTP_ACCEPT='application/json')
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['title'], 'Station 1')
        self.assertEqual(response_data['code'], 'ABC')
        self.assertEqual(response_data['constituency']['pk'], self.constituency.pk)

    def test_station_detail_put_invalid_data(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.station.pk])
        data = json.dumps({
                          'code': 'XYZ',
                          'title': '',  # Invalid: Missing title
                          'constituency': ConstituencySerializer(self.constituency).data,
                          'status': StatusChoices.ACTIVE,
                         })
        response = self.client.put(url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_station_detail_put(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.station.pk])
        data = json.dumps({
                          'code': 'XYZ',
                          'title': 'Updated Station',
                          'constituency': ConstituencySerializer(self.constituency).data,
                          'status': StatusChoices.ACTIVE,
                         })
        response = self.client.put(url, data, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.station.refresh_from_db()
        self.assertEqual(self.station.title, 'Updated Station')
        self.assertEqual(self.station.code, 'XYZ')

    def test_station_detail_delete(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse(self.endpoint_alias, args=[self.station.pk])
        response = self.client.delete(url, content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Station.objects.filter(pk=self.station.pk).exists())
