from django.test import TestCase
from __geo.models import Nation
from __geo.factories import NationFactory


class NationFactoryTestCase(TestCase):
    def test_nation_creation(self):
        nation = NationFactory()
        self.assertIsInstance(nation, Nation)
        self.assertIsNotNone(nation.id)
        self.assertIsNotNone(nation.code)
        self.assertIsNotNone(nation.title)
