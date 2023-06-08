from django.test import TestCase
from __geo.models import Constituency, Region
from __geo.factories import ConstituencyFactory, RegionFactory


class ConstituencyModelTestCase(TestCase):
    def test_station_model(self):
        # Create a station using the factory
        constituency = ConstituencyFactory(title='Test Constituency')

        # Retrieve the station from the database
        stored_constituency = Constituency.objects.get(pk=constituency.pk)

        # Assert the properties of the stored station
        self.assertEqual(stored_constituency.title, 'Test Constituency')
        self.assertIsNotNone(stored_constituency.region)
        self.assertIsNone(stored_constituency.details)
        self.assertEqual(stored_constituency.status, 'Active')
        self.assertIsNotNone(stored_constituency.created_at)    

    def test_string_representation(self):
        # Create a station using the factory
        constituency = ConstituencyFactory(title='Test Constituency')
        # Assert the string representation of the station
        self.assertEqual(str(constituency), 'Test Constituency')
