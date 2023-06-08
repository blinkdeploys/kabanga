from django.test import TestCase
from collections import OrderedDict
from __geo.models import Constituency, Region, Nation
from __geo.serializers import (
    RegionSerializer,
    NationSerializer
    #   ConstituencyCollationSerializer,
)
from __people.models import Agent, Candidate
from __geo.factories import NationFactory, RegionFactory


class RegionSerializerTest(TestCase):
    def setUp(self):
        self.nation = NationFactory(title='Example Nation')
        self.region = Region.objects.create(title='Example Region', nation=self.nation)

    def test_region_serializer(self):
        serializer = RegionSerializer(instance=self.region)
        dt = self.region.created_at
        dt = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + dt.strftime('%f')[-3:] + 'Z'
        expected_data = dict(
            pk=self.region.pk,
            title='Example Region',
            details=self.region.details,
            nation=OrderedDict(NationSerializer(instance=self.nation).data),
            agent=None,  # Expected agent data if available
            total_votes=0,  # Expected total votes value
            total_presidential_votes=0,  # Expected total presidential votes value
            total_parliamentary_votes=0,  # Expected total parliamentary votes value
            # has_presidential_approval=False,  # Expected has_presidential_approval value
            # has_parliamentary_approval=False,  # Expected has_parliamentary_approval value
            status='Active',
            created_at=dt,
        )
        self.assertEqual(serializer.data, expected_data)
