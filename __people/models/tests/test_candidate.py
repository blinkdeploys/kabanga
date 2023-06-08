from django.test import TestCase
from django.apps import apps
from __people.models import Candidate
from __poll.models import Result
from __people.factories import CandidateFactory, PartyFactory
from __poll.factories import PositionFactory
from __poll.constants import StatusChoices
from django.core.files import File
from __geo.factories import NationFactory, RegionFactory, ConstituencyFactory, StationFactory


class CandidateModelTest(TestCase):
    def setUp(self):
        # Create a Candidate instance using the factory
        zone_name = 'constituency'
        self.position = PositionFactory.create_with_zone(zone_name=zone_name)
        self.party = PartyFactory()
        self.candidate = CandidateFactory(
                                    prefix='Mr.',
                                    first_name='John',
                                    last_name='Doe',
                                    other_names='Smith',
                                    description='Sample candidate description',
                                    position=self.position,
                                    party=self.party,
                                    )

    def test_candidate_creation(self):
        candidate = self.candidate
        # Perform assertions to verify the values
        self.assertEqual(candidate.prefix, 'Mr.')
        self.assertEqual(candidate.first_name, 'John')
        self.assertEqual(candidate.last_name, 'Doe')
        self.assertEqual(candidate.other_names, 'Smith')
        self.assertEqual(candidate.description, 'Sample candidate description')
        self.assertIsInstance(candidate.photo, File)
        self.assertEqual(candidate.status, StatusChoices.ACTIVE)

        self.assertIsInstance(candidate.party, apps.get_model('__people', 'party'))
        self.assertEqual(candidate.position.title, self.position.title)

        # Test the __str__ representation
        expected_str = "Mr. John Doe Smith ({})".format(candidate.party.code)
        self.assertEqual(str(candidate), expected_str)

        # Test the full_name property
        expected_full_name = "Mr. John Doe"
        self.assertEqual(candidate.full_name, expected_full_name)

        # Test the total_votes property
        self.assertEqual(candidate.total_votes, 0)  # Assuming no results are associated

    def test_candidate_result_vote_count(self):
        try:
            nation = apps.get_model('__geo', 'nation').objects.first()
        except Exception as e:
            nation = NationFactory()
        region = RegionFactory(nation=nation)
        constituency = ConstituencyFactory(region=region)
        votes = [12,8,9,4,7,6,3,5,2,3]
        for vote in votes:
            station = StationFactory(constituency=constituency)
            result = Result(
                            station = station,
                            candidate = self.candidate,
                            votes = vote,
                            # TECH NOTE result sheet will be used for approving the vote count
                            result_sheet = None,
                            station_agent = None,
                            status = StatusChoices.ACTIVE,
                            )
            result.save()
        self.assertEqual(self.candidate.total_votes, sum(votes))

    def test_candidate_full_name_property(self):
        # Create a Candidate instance without prefix and other_names
        candidate = CandidateFactory(first_name='John', last_name='Doe')

        # Verify the full_name property when prefix and other_names are None
        expected_full_name = "M. John Doe"
        self.assertEqual(candidate.full_name, expected_full_name)
