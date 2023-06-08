from django.test import TestCase, Client
from django.urls import reverse

from __poll.constants import FormMessages
from account.models import User
from __geo.forms import ConstituencyForm
from __geo.factories import NationFactory, RegionFactory
from __geo.models import Constituency


class ConstituencyListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.nation = NationFactory()
        self.region = RegionFactory(nation=self.nation)
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_constituency_detail_unauthenticated(self):
        constituency = Constituency.objects \
                        .create(
                            title='Test Constituency 1',
                            region=self.region,
                            status='ACTIVE')
        url = reverse('constituency_detail', kwargs=dict(pk=constituency.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + url)

    def test_constituency_list_view(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('constituency_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/constituency_list.html')
        self.assertEqual(response.context['title'], 'Constituencies')
        self.assertEqual(len(response.context['data']), 0)  # No constituencies initially
        self.assertEqual(response.context['count'], 0)
        self.assertEqual(response.context['numpages'], 1)
        self.assertEqual(response.context['next_link'], '/geo/constituencies/?page=1')
        self.assertEqual(response.context['prev_link'], '/geo/constituencies/?page=1')

    def test_constituency_list_view_has_data(self):
        constituency = Constituency.objects \
                        .create(
                            title='Test Constituency 1',
                            region=self.region,
                            status='ACTIVE')
        constituency = Constituency.objects \
                        .create(
                            title='Test Constituency 2',
                            region=self.region,
                            status='ACTIVE')
        self.client.login(username='testuser', password='testpassword')
        url = reverse('constituency_list')
        response = self.client.get(url)
        self.assertEqual(len(response.context['data']), 2)

class ConstituencyDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.nation = NationFactory()
        self.region = RegionFactory(nation=self.nation)
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_constituency_detail_view_with_valid_data(self):
        self.client.login(username='testuser', password='testpassword')
        constituency = Constituency.objects \
                        .create(
                            title='Test Constituency',
                            region=self.region,
                            status='ACTIVE')
        url = reverse('constituency_detail', kwargs=dict(pk=constituency.pk))
        data = dict(title='Updated Constituency',
                    region=self.region.pk,
                    status='Active')
        response = self.client.post(url, data, follow=True)
        context = response.context
        message = context['message']
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/constituency_form.html')
        self.assertEqual(int(context['pk']), constituency.pk)
        self.assertEqual(context['title'], 'Constituency')
        self.assertEqual(context['detail_path'], 'constituency_detail')
        self.assertIsInstance(context['elements'], ConstituencyForm)
        constituency.refresh_from_db()
        self.assertEqual(message, FormMessages.SUCCESS)
        self.assertEqual(constituency.title, 'Updated Constituency')

    def test_constituency_detail_view_with_invalid_data(self):
        self.client.login(username='testuser', password='testpassword')
        constituency = Constituency.objects \
                        .create(
                            title='Test Constituency', 
                            region=self.region,
                            status='Active')
        url = reverse('constituency_detail', kwargs=dict(pk=constituency.pk))
        data = dict(title='',
                    region=self.region.pk,
                    status='Active')
        response = self.client.post(url, data, follow=True)
        context = response.context
        message = context['message']

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/constituency_form.html')
        self.assertEqual(int(context['pk']), constituency.pk)
        self.assertEqual(context['title'], 'Constituency')
        self.assertEqual(context['detail_path'], 'constituency_detail')
        self.assertEqual(context['list_path'], 'constituency_list')
        self.assertIn(FormMessages.INVALID_FORM, message)
