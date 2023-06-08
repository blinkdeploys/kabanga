from django.test import TestCase
from collections import OrderedDict
from rest_framework import serializers
from __geo.models import Station, Constituency, Region, Nation
from __geo.serializers import (
    StationSerializer, StationCollationSerializer, StationSubmitSerializer,
    ConstituencySerializer
)
from __people.models import Agent, Candidate
from __poll.utils.utils import get_zone_ct
from __geo.factories import NationFactory, RegionFactory, ConstituencyFactory


class StationSerializerTest(TestCase):
    def setUp(self):
        self.nation = NationFactory(title='Example Nation')
        self.region = RegionFactory(title='Example Region', nation=self.nation)
        self.constituency = ConstituencyFactory(title='Example Constituency', region=self.region)
        self.station = Station.objects.create(code='S001', title='Example Station', constituency=self.constituency)

    def test_station_serializer(self):
        serializer = StationSerializer(instance=self.station)
        dt = self.station.created_at
        dt = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + dt.strftime('%f')[-3:] + 'Z'
        expected_data = {
            'pk': self.station.pk,
            'code': 'S001',
            'title': 'Example Station',
            'details': self.station.details,
            'constituency': OrderedDict(ConstituencySerializer(instance=self.constituency).data),
            'agent': None,  # Expected agent data if available
            'total_votes': 0,  # Expected total votes value
            'total_presidential_votes': 0,  # Expected total presidential votes value
            'total_parliamentary_votes': 0,  # Expected total parliamentary votes value
            'has_presidential_approval': False,  # Expected has_presidential_approval value
            'has_parliamentary_approval': False,  # Expected has_parliamentary_approval value
            'status': 'Active',
            'created_at': dt,
        }
        self.assertEqual(serializer.data, expected_data)


class StationCollationSerializerTest(TestCase):
    def setUp(self):
        self.nation = NationFactory(title='Example Nation')
        self.region = RegionFactory(title='Example Region', nation=self.nation)
        self.constituency = ConstituencyFactory(title='Example Constituency', region=self.region)
        self.station = Station.objects.create(code='S001', title='Example Station', constituency=self.constituency)

    def test_station_collation_serializer(self):
        serializer = StationCollationSerializer(instance=self.station)
        dt = self.station.created_at
        dt = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + dt.strftime('%f')[-3:] + 'Z'
        expected_data = {
            'pk': self.station.pk,
            'code': 'S001',
            'title': 'Example Station',
            'votes': 0,  # Expected votes value
            'constituency': OrderedDict(ConstituencySerializer(instance=self.constituency).data),
            'agent': None,  # Expected agent data if available
            'status': 'Active',
            'created_at': dt,
        }
        self.assertEqual(serializer.data, expected_data)


class StationSubmitSerializerTest(TestCase):
    def setUp(self):
        nation = NationFactory()
        region = RegionFactory(nation=nation)
        self.constituency = Constituency.objects.create(title='Constituency 1', region=region)
        self.valid_data = {
                            'code': 'ABC',
                            'title': 'Station 1',
                            'constituency': {
                                'pk': self.constituency.pk,
                                'title': self.constituency.title
                            },
                            'status': 'Active',
                          }
        self.serializer = StationSubmitSerializer(data=self.valid_data)

    def test_valid_data(self):
        self.assertTrue(self.serializer.is_valid())

    def test_empty_code(self):
        data = self.valid_data.copy()
        data['code'] = ''
        serializer = StationSubmitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['code'], ['This field may not be blank.'])

    def test_empty_title(self):
        data = self.valid_data.copy()
        data['title'] = ''
        serializer = StationSubmitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['title'], ['This field may not be blank.'])

    def test_empty_status(self):
        data = self.valid_data.copy()
        data['status'] = ''
        serializer = StationSubmitSerializer(data=data)
        expected_error = ' is not a valid choice.'
        self.assertFalse(serializer.is_valid())
        self.assertIn(expected_error, str(serializer.errors['status'][0]))

    def test_empty_constituency(self):
        data = self.valid_data.copy()
        data['constituency'] = {}
        serializer = StationSubmitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['non_field_errors'], ['constituency cannot be empty.'])

    def test_invalid_constituency_pk(self):
        data = self.valid_data.copy()
        data['constituency']['pk'] = 0
        serializer = StationSubmitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['non_field_errors'], ['constituency cannot be empty.'])

    def test_create_station(self):
        self.assertTrue(self.serializer.is_valid())
        station = self.serializer.save()
        self.assertIsInstance(station, Station)
        self.assertEqual(station.code, self.valid_data['code'])
        self.assertEqual(station.title, self.valid_data['title'])
        self.assertEqual(station.constituency, self.constituency)
        self.assertEqual(station.status, self.valid_data['status'])
