from django.test import TestCase, Client
from django.urls import reverse

from __poll.constants import FormMessages
from account.models import User
from __geo.forms import StationForm
from __geo.factories import NationFactory, RegionFactory, ConstituencyFactory
from __geo.models import Station


class StationListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.nation = NationFactory()
        self.region = RegionFactory(nation=self.nation)
        self.constituency = ConstituencyFactory(region=self.region)
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_station_detail_unauthenticated(self):
        station = Station.objects \
                        .create(
                            title='Test Station 1',
                            constituency=self.constituency,
                            status='ACTIVE')
        url = reverse('station_detail', kwargs=dict(pk=station.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + url)

    def test_station_list_view(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('station_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/station_list.html')
        self.assertEqual(response.context['title'], 'Stations')
        self.assertEqual(len(response.context['data']), 0)  # No stations initially
        self.assertEqual(response.context['count'], 0)
        self.assertEqual(response.context['numpages'], 1)
        self.assertEqual(response.context['next_link'], '/geo/stations/?page=1')
        self.assertEqual(response.context['prev_link'], '/geo/stations/?page=1')

    def test_station_list_view_has_data(self):
        station = Station.objects \
                        .create(
                            title='Test Station 1',
                            constituency=self.constituency,
                            status='ACTIVE')
        station = Station.objects \
                        .create(
                            title='Test Station 2',
                            constituency=self.constituency,
                            status='ACTIVE')
        self.client.login(username='testuser', password='testpassword')
        url = reverse('station_list')
        response = self.client.get(url)
        self.assertEqual(len(response.context['data']), 2)


class StationDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.nation = NationFactory()
        self.region = RegionFactory(nation=self.nation)
        self.constituency = ConstituencyFactory(region=self.region)
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_station_detail_view_with_valid_data(self):
        self.client.login(username='testuser', password='testpassword')
        station = Station.objects \
                        .create(
                            title='Test Station',
                            constituency=self.constituency,
                            status='ACTIVE')
        url = reverse('station_detail', kwargs=dict(pk=station.pk))
        data = dict(title='Updated Station',
                    code='SU',
                    constituency=self.constituency.pk,
                    details='more station details',
                    status='Active')
        response = self.client.post(url, data, follow=True)
        context = response.context
        message = context['message']
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/station_form.html')
        self.assertEqual(int(context['pk']), station.pk)
        self.assertEqual(context['title'], 'Station')
        self.assertEqual(context['detail_path'], 'station_detail')
        self.assertIsInstance(context['elements'], StationForm)
        station.refresh_from_db()
        self.assertEqual(message, FormMessages.SUCCESS)
        self.assertEqual(station.title, 'Updated Station')
        self.assertEqual(station.code, 'SU')

    def test_station_detail_view_with_invalid_data(self):
        self.client.login(username='testuser', password='testpassword')
        station = Station.objects \
                        .create(
                            title='Test Station', 
                            constituency=self.constituency,
                            status='Active')
        url = reverse('station_detail', kwargs=dict(pk=station.pk))
        data = dict(title='',
                    region=self.region.pk,
                    status='Active')
        response = self.client.post(url, data, follow=True)
        context = response.context
        message = context['message']
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/station_form.html')
        self.assertEqual(int(context['pk']), station.pk)
        self.assertEqual(context['title'], 'Station')
        self.assertEqual(context['detail_path'], 'station_detail')
        self.assertEqual(context['list_path'], 'station_list')
        self.assertIn(FormMessages.INVALID_FORM, message)
