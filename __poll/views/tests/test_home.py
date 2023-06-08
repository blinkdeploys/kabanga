from django.test import TestCase, Client
from django.contrib.auth.models import AnonymousUser
from account.models import User
from django.urls import reverse

class HomeViewTestCase(TestCase):
    def test_anonymous_user_redirect(self):
        client = Client()
        response = client.get(reverse('home'))
        expected_redirect_url = '/accounts/login/'
        self.assertEqual(response.status_code, 302)
        self.assertIn(expected_redirect_url, response.url)

    def test_authenticated_user_view(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Poll Results')
        self.assertContains(response, 'Enter election results from polling stations.')
        self.assertContains(response, '/poll/result/stations/')
        self.assertContains(response, 'Approve Results')
        self.assertContains(response, 'Approve and publish election results at polling stations.')
        self.assertContains(response, '/poll/result_approvals/')
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'View polling results dashboard and party performance.')
        self.assertContains(response, '/reports/dashboard')
        self.assertContains(response, 'View Reports')
        self.assertContains(response, 'View election results from collated results at all geo levels.')
        self.assertContains(response, '/reports')
        self.assertContains(response, 'Review Agents')
        self.assertContains(response, 'Review all party agents at all levels.')
        self.assertContains(response, '/people/agents')
        self.assertContains(response, 'Review Candidates')
        self.assertContains(response, 'Manage candidate / party data.')
        self.assertContains(response, '/people/candidates')
        self.assertContains(response, 'Location Setup')
        self.assertContains(response, 'Manage regions, constituencies and polling stations.')
        self.assertContains(response, '/geo')
        self.assertContains(response, 'Review Election Events')
        self.assertContains(response, 'Update election dates and events')
        self.assertContains(response, '#')
