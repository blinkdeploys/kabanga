from django.test import TestCase
from __geo.models import Station, Constituency
from __geo.factories import StationFactory, ConstituencyFactory


class StationModelTestCase(TestCase):
    def test_station_model(self):
        # Create a station using the factory
        station = StationFactory(title='Test Station', code='TEST123')

        # Retrieve the station from the database
        stored_station = Station.objects.get(pk=station.pk)

        # Assert the properties of the stored station
        self.assertEqual(stored_station.title, 'Test Station')
        self.assertEqual(stored_station.code, 'TEST123')
        self.assertIsNotNone(stored_station.constituency)
        self.assertIsNone(stored_station.details)
        self.assertEqual(stored_station.status, 'Active')
        self.assertIsNotNone(stored_station.created_at)    

    def test_string_representation(self):
        # Create a station using the factory
        station = StationFactory(title='Test Station', code='TEST123')
        # Assert the string representation of the station
        self.assertEqual(str(station), 'TEST123 Test Station')

    def test_station_has_constituency(self):
        # Create a constituency
        constituency = ConstituencyFactory()
        # Create a station associated with the constituency
        station = StationFactory(constituency=constituency)
        # Retrieve the station from the database
        stored_station = Station.objects.get(pk=station.pk)
        # Assert the constituency relationship
        self.assertEqual(stored_station.constituency, constituency)
