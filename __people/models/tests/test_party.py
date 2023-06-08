from unittest import TestCase
from django.test import TestCase
from django.apps import apps

from __poll.utils.utils import get_zone_ct
from __people.models import Party
from __poll.models import Result, SupernationalCollationSheet
from __geo.factories import NationFactory, RegionFactory, ConstituencyFactory, StationFactory
from __people.factories import PartyFactory, CandidateFactory
from __poll.constants import StatusChoices


class PartyModelTest(TestCase):
    def test_str_representation(self):
        party = PartyFactory(code='ABC', title='Test Party')
        self.assertEqual(str(party), 'Test Party (ABC)')

    def test_total_candidates(self):
        party = PartyFactory(code='ABC', title='Test Party')
        party.save()
        for i in range(0, 4):
            CandidateFactory(party=party)
        # Add necessary candidates related to the party
        total_candidates = party.total_candidates()
        # Assert the expected total candidates count
        self.assertEqual(total_candidates, 4)


class PartyModelCollationCountsTest(TestCase):
    def setUp(self):
        try:
            nation = apps.get_model('nation').objects.first()
        except Exception as e:
            nation = NationFactory()
        self.party = PartyFactory(code='ABC', title='Test Party')
        self.party.save()
        self.votes = dict(
                          nation=[12, 9, 8, 7, 4, 15, 6],
                          constituency=[5, 4, 6, 5, 23, 4, 5, 3, 6],
                         )
        self.total_presidential_votes = sum(self.votes.get('nation', []))
        self.total_parliamentary_votes = sum(self.votes.get('constituency', []))
        self.total_votes = self.total_presidential_votes + self.total_parliamentary_votes
        for k, v in self.votes.items():
            zone_ct = get_zone_ct(apps.get_model('__geo', k))
            for total_vote in v:
                collation = SupernationalCollationSheet(
                    party=self.party,
                    nation=nation,
                    total_votes = total_vote,
                    total_invalid_votes = 3,
                    total_votes_ec = 22,
                    status = StatusChoices.ACTIVE,
                    zone_ct = zone_ct,
                )
                collation.save()

    def test_result_votes(self):
        # Add necessary supernational_collation_sheets related to the party
        result_votes = self.party.result_votes
        # Assert the expected result votes
        self.assertEqual(result_votes, self.total_votes)

    def test_total_presidential_votes(self):
        # Add necessary supernational_collation_sheets related to the party
        total_presidential_votes = self.party.total_presidential_votes
        # Assert the expected total presidential votes
        self.assertEqual(total_presidential_votes, self.total_presidential_votes)

    def test_total_parliamentary_votes(self):
        # Add necessary supernational_collation_sheets related to the party
        total_parliamentary_votes = self.party.total_parliamentary_votes
        # Assert the expected total parliamentary votes
        self.assertEqual(total_parliamentary_votes, self.total_parliamentary_votes)


'''
        region = RegionFactory(nation=nation)
        constituency = ConstituencyFactory(region=region)
        station1 = StationFactory(constituency=constituency)
        constituency = ConstituencyFactory(region=region)
        station2 = StationFactory(constituency=constituency)
        constituency = ConstituencyFactory(region=region)
        station3 = StationFactory(constituency=constituency)
        constituency = ConstituencyFactory(region=region)
        station4 = StationFactory(constituency=constituency)
        candidate1 = CandidateFactory(party=party)
        candidate2 = CandidateFactory(party=party)
        candidate3 = CandidateFactory(party=party)
        candidate4 = CandidateFactory(party=party)
        Result(station=station1, candidate=candidate1, votes=25)
        Result(station=station2, candidate=candidate2, votes=25)
        Result(station=station3, candidate=candidate3, votes=25)
        Result(station=station4, candidate=candidate4, votes=25)
'''

