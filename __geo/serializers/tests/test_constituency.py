from django.test import TestCase
from collections import OrderedDict
from __geo.models import Constituency, Region, Nation
from __geo.serializers import (
    ConstituencySerializer,
    RegionSerializer
    #   ConstituencyCollationSerializer,
)
from __people.models import Agent, Candidate
from __geo.factories import NationFactory, RegionFactory


class ConstituencySerializerTest(TestCase):
    def setUp(self):
        self.nation = NationFactory(title='Example Nation')
        self.region = RegionFactory(title='Example Region', nation=self.nation)
        self.constituency = Constituency.objects.create(title='Example Constituency', region=self.region)

    def test_constituency_serializer(self):
        serializer = ConstituencySerializer(instance=self.constituency)
        dt = self.constituency.created_at
        dt = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + dt.strftime('%f')[-3:] + 'Z'
        expected_data = {
            'pk': self.constituency.pk,
            'title': 'Example Region',
            'region': OrderedDict(RegionSerializer(instance=self.region).data),
            'total_votes': 0,  # Expected total votes value
            'total_presidential_votes': 0,  # Expected total presidential votes value
            'total_parliamentary_votes': 0,  # Expected total parliamentary votes value
            # 'has_presidential_approval': False,  # Expected has_presidential_approval value
            # 'has_parliamentary_approval': False,  # Expected has_parliamentary_approval value
            'status': 'Active',
            'agent': None,  # Expected agent data if available
            'created_at': dt,
        }
        self.assertEqual(serializer.data, expected_data)

'''
class ConstituencyCollationSerializerTest(TestCase):
    def setUp(self):
        self.nation = NationFactory(title='Example Nation')
        self.region = RegionFactory(title='Example Region', nation=self.nation)
        self.constituency = Constituency.objects.create(code='S001', title='Example Constituency', region=self.region)

    def test_constituency_collation_serializer(self):
        serializer = ConstituencyCollationSerializer(instance=self.constituency)
        dt = self.constituency.created_at
        dt = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + dt.strftime('%f')[-3:] + 'Z'
        expected_data = {
            'pk': self.constituency.pk,
            'code': 'S001',
            'title': 'Example Region',
            'votes': 0,  # Expected votes value
            'region': OrderedDict(RegionSerializer(instance=self.region).data),
            'agent': None,  # Expected agent data if available
            'status': 'Active',
            'created_at': dt,
        }
        self.assertEqual(serializer.data, expected_data)
'''
