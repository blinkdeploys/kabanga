from django.test import TestCase
from __geo.models import Region
from __geo.factories import RegionFactory


class RegionFactoryTestCase(TestCase):
    def test_region_creation(self):
        region = RegionFactory(title="Nation A")
        self.assertIsInstance(region, Region)
        self.assertIsNotNone(region.id)
        self.assertEqual(region.title, "Nation A")
