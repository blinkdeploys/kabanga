from django.test import TestCase
from __geo.models import Nation
from __geo.factories import NationFactory
from django.core.exceptions import ValidationError


class NationModelTestCase(TestCase):
    def test_string_representation(self):
        nation = Nation(code='ABC', title='Nation A')
        self.assertEqual(str(nation), 'Nation A')

    def test_single_instance_limit(self):
        # Create an initial Nation instance
        nation = Nation(code='ABC', title='Nation A')
        nation.save()

        # Try to create a new Nation instance, which should raise a ValidationError
        with self.assertRaises(ValidationError):
            nation2 = Nation(code='XYZ', title='Nation B')
            nation2.save()

        # Ensure that only one instance of Nation exists in the database
        self.assertEqual(Nation.objects.count(), 1)
