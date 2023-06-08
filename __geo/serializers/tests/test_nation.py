from django.test import TestCase
from collections import OrderedDict
from __geo.models import Nation
from __geo.serializers import NationSerializer
from __people.models import Agent, Candidate
from __geo.factories import NationFactory, RegionFactory


class NationSerializerTest(TestCase):
    def setUp(self):
        self.nation = Nation.objects.create(code='NE', title='Example Nation')

    def test_nation_serializer(self):
        serializer = NationSerializer(instance=self.nation)
        # dt = self.nation.created_at
        # dt = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + dt.strftime('%f')[-3:] + 'Z'
        expected_data = dict(
            pk=self.nation.pk,
            code='NE',
            title='Example Nation',
            agent=None,  # Expected agent data if available
            total_votes=0,  # Expected total votes value
            total_presidential_votes=0,  # Expected total presidential votes value
            total_parliamentary_votes=0,  # Expected total parliamentary votes value
            # has_presidential_approval=False,  # Expected has_presidential_approval value
            # has_parliamentary_approval=False,  # Expected has_parliamentary_approval value
            # status='Active',
            # created_at=dt,
        )
        self.assertEqual(serializer.data, expected_data)
