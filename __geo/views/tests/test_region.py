from django.test import TestCase, Client
from django.urls import reverse
from account.models import User
from __geo.models import Region
from __geo.factories import NationFactory
from __geo.forms import RegionForm
from __poll.constants import FormMessages


class RegionListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.nation = NationFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_constituency_list_unauthenticated(self):
        region = Region.objects \
                        .create(
                            title='Test Region 1',
                            nation=self.nation,
                            status='ACTIVE')
        url = reverse('region_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + url)

    def test_region_list_view(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('region_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/region_list.html')
        self.assertEqual(response.context['title'], 'Regions')
        self.assertEqual(len(response.context['data']), 0)  # No regions initially
        self.assertEqual(response.context['count'], 0)
        self.assertEqual(response.context['numpages'], 1)
        self.assertEqual(response.context['next_link'], '/geo/regions/?page=1')
        self.assertEqual(response.context['prev_link'], '/geo/regions/?page=1')

    def test_region_list_view_has_data(self):
        region = Region.objects \
                        .create(
                            title='Test Region 1',
                            nation=self.nation,
                            status='ACTIVE')
        region = Region.objects \
                        .create(
                            title='Test Region 2',
                            nation=self.nation,
                            status='ACTIVE')
        self.client.login(username='testuser', password='testpassword')
        url = reverse('region_list')
        response = self.client.get(url)
        self.assertEqual(len(response.context['data']), 2)


class RegionDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.nation = NationFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_region_detail_view_with_valid_data(self):
        self.client.login(username='testuser', password='testpassword')
        region = Region.objects \
                        .create(
                            title='Test Region',
                            nation=self.nation,
                            status='ACTIVE')
        url = reverse('region_detail', kwargs=dict(pk=region.pk))
        data = dict(title='Updated Region',
                    nation=self.nation.pk,
                    status='Active')
        response = self.client.post(url, data, follow=True)
        context = response.context
        message = context['message']
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/region_form.html')
        self.assertEqual(int(context['pk']), region.pk)
        self.assertEqual(context['title'], 'Region')
        self.assertEqual(context['detail_path'], 'region_detail')
        self.assertIsInstance(context['elements'], RegionForm)
        # self.assertEqual(context['elements'].initial['pk'], region.pk)
        # self.assertEqual(context['elements'].initial['title'], region.title)
        # self.assertEqual(context['elements'].initial['nation'], region.nation)
        # self.assertEqual(context['elements'].initial['status'], region.status)
        region.refresh_from_db()
        self.assertEqual(message, FormMessages.SUCCESS)
        self.assertEqual(region.title, 'Updated Region')

    def test_region_detail_view_with_invalid_data(self):
        self.client.login(username='testuser', password='testpassword')
        region = Region.objects \
                        .create(
                            title='Test Region', 
                            nation=self.nation,
                            status='Active')
        url = reverse('region_detail', kwargs=dict(pk=region.pk))
        data = dict(title='',
                    nation=self.nation.pk,
                    status='Active')
        response = self.client.post(url, data, follow=True)
        context = response.context
        message = context['message']

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/region_form.html')
        self.assertEqual(int(context['pk']), region.pk)
        self.assertEqual(context['title'], 'Region')
        self.assertEqual(context['detail_path'], 'region_detail')
        self.assertEqual(context['list_path'], 'region_list')
        self.assertIn(FormMessages.INVALID_FORM, message)
