from django.test import TestCase
from __geo.models import Region, Nation, Station
from django.db.models import Prefetch
from __geo.factories import RegionFactory, ConstituencyFactory, StationFactory


class RegionModelTestCase(TestCase):
    def test_region_model(self):
        # Create a region using the factory
        region = RegionFactory(title='Test Region')

        # Retrieve the region from the database
        stored_region = Region.objects.get(pk=region.pk)

        # Assert the properties of the stored region
        self.assertEqual(stored_region.title, 'Test Region')
        self.assertIsNone(stored_region.details)
        self.assertEqual(stored_region.status, 'Active')
        self.assertIsNotNone(stored_region.created_at)

        # Assert the constituencies relationship
        self.assertQuerysetEqual(stored_region.constituencies.all(), [])

    def test_string_representation(self):
        # Create a region using the factory
        region = RegionFactory(title='Test Region')

        # Assert the string representation of the region
        self.assertEqual(str(region), 'Test Region')

    def test_stations_property(self):
        # Create a region using the factory
        region = RegionFactory(title='Test Region')

        # Create constituencies associated with the region
        constituency1 = ConstituencyFactory(region=region)
        constituency2 = ConstituencyFactory(region=region)

        # Create stations associated with the constituencies
        station1 = StationFactory(constituency=constituency1)
        station2 = StationFactory(constituency=constituency2)

        # Retrieve the region from the database
        stored_region = Region.objects.get(pk=region.pk)

        # Access the stations property of the region
        stations = stored_region.stations

        # Assert the stations associated with the region
        self.assertEqual(len(stations), 2)
        self.assertIn(station1, stations)
        self.assertIn(station2, stations)
