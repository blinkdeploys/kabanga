from django.test import TestCase, Client
from django.urls import reverse
from account.models import User
from __people.models import Candidate, Party
from __poll.models import Position
from __poll.constants import FormMessages
from __people.forms import CandidateForm
from django.contrib.messages import get_messages
from __poll.factories import PositionFactory
from __people.factories import PartyFactory, CandidateFactory


class CandidateListTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # self.position = Position.objects.create(title='Test Position')
        # self.party = Party.objects.create(code='TP', title='Test Party')
        zone_name = 'constituency'
        self.position = PositionFactory.create_with_zone(zone_name=zone_name)
        self.party = PartyFactory()

    def test_candidate_list_unauthenticated(self):
        self.candidate = CandidateFactory(
                                    prefix='Mr.',
                                    first_name='John',
                                    last_name='Doe',
                                    other_names='Smith',
                                    description='Sample candidate description',
                                    position=self.position,
                                    party=self.party,
                                    )
        url = reverse('candidate_list')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + url)

    def test_candidate_list_view(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('candidate_list')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'people/candidate_list.html')
        self.assertEqual(response.context['title'], 'Candidates')
        self.assertEqual(len(response.context['data']), 0)
        self.assertEqual(response.context['count'], 0)
        self.assertEqual(response.context['numpages'], 1)
        self.assertEqual(response.context['next_link'], '/people/candidates/?page=1')
        self.assertEqual(response.context['prev_link'], '/people/candidates/?page=1')

    def test_candidate_list_view_has_data(self):
        self.candidate = CandidateFactory(
                                    prefix='Ms.',
                                    first_name='Jane',
                                    last_name='Dane',
                                    other_names='Kroker',
                                    description='Sample candidate description',
                                    position=self.position,
                                    party=self.party,
                                    )
        self.candidate = CandidateFactory(
                                    prefix='Mr.',
                                    first_name='John',
                                    last_name='Doe',
                                    other_names='Smith',
                                    description='Second sample candidate description',
                                    position=self.position,
                                    party=self.party,
                                    )
        self.candidate = CandidateFactory(
                                    prefix='Mr.',
                                    first_name='Jack',
                                    last_name='Dill',
                                    other_names='Xavier',
                                    description='Third sample candidate description',
                                    position=self.position,
                                    party=self.party,
                                    )
        self.client.login(username='testuser', password='testpassword')
        url = reverse('candidate_list')
        response = self.client.get(url, follow=True)
        self.assertEqual(len(response.context['data']), 3)

    def test_candidate_list(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('candidate_list')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'people/candidate_list.html')
        Candidate.objects.create(prefix='Mr', first_name='John', last_name='Doe', position=self.position, party=self.party)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['data']), 1)


class CandidateDetailTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.candidate = Candidate(prefix='Mr', first_name='John', last_name='Doe')
        self.candidate.save()

    def test_candidate_detail_get(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('candidate_detail', kwargs={'pk': self.candidate.pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Candidate')
        self.assertContains(response, 'Cancel')
        self.assertContains(response, 'Save')
        self.assertTemplateUsed(response, 'people/candidate_form.html')
        self.assertIsInstance(response.context['form'], CandidateForm)
        form = response.context['form']
        self.assertEqual(form.initial['pk'], self.candidate.pk)
        self.assertEqual(form.initial['prefix'], self.candidate.prefix)
        self.assertEqual(form.initial['first_name'], self.candidate.first_name)
        self.assertEqual(form.initial['last_name'], self.candidate.last_name)
        self.assertEqual(form.initial['other_names'], self.candidate.other_names)
        self.assertEqual(form.initial['description'], self.candidate.description)
        self.assertEqual(form.initial['position'], self.candidate.position)
        self.assertEqual(form.initial['party'], self.candidate.party)
        self.assertEqual(form.initial['status'], self.candidate.status)

    def test_candidate_detail_post_invalid_data(self):
        position = Position.objects.create(title='Test Position')
        party = Party.objects.create(code='TPP', title='Test Political Party')
        self.client.login(username='testuser', password='testpassword')
        url_kwargs = {'pk': self.candidate.pk}
        url = reverse('candidate_detail', kwargs=url_kwargs)
        data = dict(
                    prefix='Mr',
                    first_name='',
                    last_name='',
                    position=position,
                    party=party,
                    )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(FormMessages.INVALID_FORM, str(messages[0]))
        validation_messages = [
                                {
                                'title': 'first name',
                                'template': FormMessages.INVALID_REQUIRED,
                                },
                                {
                                'title': 'last name',
                                'template': FormMessages.INVALID_REQUIRED,
                                },
                                {
                                'title': 'position',
                                'template': FormMessages.INVALID_CHOICE,
                                },
                                {
                                'title': 'party',
                                'template': FormMessages.INVALID_CHOICE,
                                }
                              ]
        all_messages = str(messages[0]).lower()
        for validation_message in validation_messages:
            expected = validation_message['template'] \
                                   .format(validation_message['title']) \
                                   .lower()
            with self.subTest():
               self.assertIn(expected, all_messages)

    def test_candidate_detail_post_valid_data(self):
        position = Position(title='Test Position')
        position.save()
        party = Party(code='TPP', title='Test Political Party')
        party.save()
        self.client.login(username='testuser', password='testpassword')
        url = reverse('candidate_detail', kwargs={'pk': self.candidate.pk})
        data = dict(
                    prefix='Mr.',
                    first_name='Jack',
                    last_name='Dule',
                    other_names='Xavier',
                    position=position.pk,
                    party=party.pk,
                    )
        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, url)
        self.assertIsInstance(response.context['form'], CandidateForm)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), FormMessages.SUCCESS)

        self.candidate.refresh_from_db()
        self.assertRedirects(response, reverse('candidate_detail', kwargs={'pk': self.candidate.pk}))
        self.assertEqual(self.candidate.prefix, 'Mr.')
        self.assertEqual(self.candidate.first_name, 'Jack')
        self.assertEqual(self.candidate.last_name, 'Dule')
        self.assertEqual(self.candidate.other_names, 'Xavier')
        self.assertIsInstance(self.candidate.position, type(position))
        self.assertEqual(self.candidate.position.pk, position.pk)
        self.assertIsInstance(self.candidate.party, type(party))
        self.assertEqual(self.candidate.party.pk, party.pk)
