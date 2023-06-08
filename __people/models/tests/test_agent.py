from django.test import TestCase
from django.apps import apps
from __people.factories import AgentFactory


class AgentModelTest(TestCase):
    def setUp(self):
        self.agent = AgentFactory.create_with_zone(zone_name='constituency',
                                              **dict(
                                                        first_name='John',
                                                        last_name='Doe',
                                                        email='john.doe@example.com',
                                                        phone='1234567890',
                                                        address='123 Main St',
                                                    ))
    def test_agent_creation(self):
        self.assertEqual(self.agent.first_name, 'John')
        self.assertEqual(self.agent.last_name, 'Doe')
        self.assertEqual(self.agent.email, 'john.doe@example.com')
        self.assertEqual(self.agent.phone, '1234567890')
        self.assertEqual(self.agent.address, '123 Main St')
        self.assertEqual(self.agent.full_name, 'John Doe')

    def test_agent_properties(self):
        self.assertEqual(str(self.agent), 'John Doe')
        self.assertIsInstance(self.agent.zone, apps.get_model('__geo', 'constituency'))
        self.assertEqual(self.agent.zone_type, 'Constituency')
        self.assertEqual(self.agent.zone_title, self.agent.zone.title)


class AgentWIthoutZoneModelTest(TestCase):
    def setUp(self):
        self.agent = AgentFactory()

    def test_agent_without_zone(self):
        self.assertEqual(self.agent.zone_title, '')
        self.assertEqual(self.agent.zone_type, 'N/A')
