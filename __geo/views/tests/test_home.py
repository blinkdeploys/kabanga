from django.test import TestCase, Client
from django.contrib.auth.models import AnonymousUser
from account.models import User
from django.urls import reverse

class HomeViewTestCase(TestCase):
    def test_anonymous_user_redirect(self):
        client = Client()
        response = client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


    def test_authenticated_user_view(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('geo_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Polling Stations')
        self.assertContains(response, '/geo/stations')
        self.assertContains(response, 'Manage polling stations')
        self.assertContains(response, 'Nation')
        self.assertContains(response, '/geo/nations')
        self.assertContains(response, 'Manage nation details')
        self.assertContains(response, 'Constituencies')
        self.assertContains(response, '/geo/constituencies')
        self.assertContains(response, 'Manage constituencies')
        self.assertContains(response, 'Regions')
        self.assertContains(response, '/geo/regions')
        self.assertContains(response, 'Manage regions')
