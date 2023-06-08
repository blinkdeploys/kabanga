from django.test import TestCase
from __geo.factories import StationFactory


class StationFactoryTestCase(TestCase):
    def test_station_factory(self):
        # Create a station using the factory
        station = StationFactory(title='Test Station', code='TEST123')

        # Assert the properties of the created station
        self.assertEqual(station.title, 'Test Station')
        self.assertEqual(station.code, 'TEST123')
