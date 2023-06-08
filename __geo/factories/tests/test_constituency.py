from django.test import TestCase
from django.db.utils import IntegrityError
from __geo.factories import ConstituencyFactory

class ConstituencyFactoryTestCase(TestCase):
    def test_raises_error_on_null_region(self):
        with self.assertRaises(IntegrityError):
            ConstituencyFactory(title=None)

    def test_constituency_factory(self):
        # Create a station using the factory
        constituency = ConstituencyFactory(title='Test Station')
        # Assert the properties of the created station
        self.assertEqual(constituency.title, 'Test Station')
        self.assertIsNotNone(constituency.region)
