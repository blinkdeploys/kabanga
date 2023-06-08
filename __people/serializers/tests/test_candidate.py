from django.test import TestCase
from rest_framework import serializers
from django.core.files.uploadedfile import SimpleUploadedFile

from __people.serializers import CandidateSerializer, CandidateDetailSerializer, PartyAsChildSerializer
from __people.models import Candidate
from __poll.serializers import PositionSerializer
from __people.factories import PartyFactory
from __poll.factories import PositionFactory

DEFAULT_IMAGE_PATH = 'static/blank.png'


class CandidateDetailSerializerTest(TestCase):
    def test_serializer_valid_data(self):
        party = PartyFactory()
        position = PositionFactory.create_with_zone('constituency')
        party.save()
        position.save()
        party_data = PartyAsChildSerializer(party).data
        position_data = PositionSerializer(position).data

        image_file = open(DEFAULT_IMAGE_PATH, 'rb')
        file_data = {
            'photo': SimpleUploadedFile('photo.jpg', image_file.read()),
            # Add other required file fields if any
        }
        serializer_data = {
                           'pk': 1,
                           # 'photo': file_data['photo'],
                           'photo': DEFAULT_IMAGE_PATH,
                           'first_name': 'John',
                           'last_name': 'Doe',
                           'party': party_data,
                           'position': position_data,
                           'total_votes': 10,
                           'description': 'Candidate description',
                           'status': 'Active',
                           'created_at': '2023-05-26T12:00:00',
                          }
        serializer = CandidateDetailSerializer(data=serializer_data)
        serializer_is_valid = serializer.is_valid()
        self.assertTrue(serializer_is_valid)

    def test_serializer_invalid_data(self):
        serializer_data = {
            'pk': 1,
            'photo': DEFAULT_IMAGE_PATH,
            'first_name': 'John',
            'last_name': 'Doe',
            'party': None,  # Invalid, party cannot be empty
            'position': None,  # Invalid, position cannot be empty
            'total_votes': 10,
            'description': 'Candidate description',
            'status': 'active',
            'created_at': '2023-05-26T12:00:00',
        }
        DEFAULT_VALIDATION_ERROR = 'This field may not be null.'
        serializer = CandidateDetailSerializer(data=serializer_data)
        serializer_is_valid = serializer.is_valid()
        self.assertFalse(serializer_is_valid)
        self.assertIn('party', serializer.errors)
        self.assertIn('position', serializer.errors)
        self.assertEqual(
            serializer.errors['party'][0],
            DEFAULT_VALIDATION_ERROR
        )
        self.assertEqual(
            serializer.errors['position'][0],
            DEFAULT_VALIDATION_ERROR
        )


class CandidateSerializerTest(TestCase):
    def test_serializer_valid_data(self):
        party = PartyFactory()
        position = PositionFactory.create_with_zone('constituency')
        party.save()
        position.save()
        party_data = PartyAsChildSerializer(party).data
        position_data = PositionSerializer(position).data
        serializer_data = {
                           'pk': 1,
                           'photo': DEFAULT_IMAGE_PATH,
                           'full_name': 'John Doe',
                           'party': party_data,
                           'position': position_data,
                           'total_votes': 10,
                           'description': 'Candidate description',
                           'status': 'Active',
                           'created_at': '2023-05-26T12:00:00',
                          }
        serializer = CandidateSerializer(data=serializer_data)
        serializer_is_valid = serializer.is_valid()
        self.assertTrue(serializer_is_valid)

    def test_serializer_invalid_data(self):
        serializer_data = {
            'pk': 1,
            'photo': DEFAULT_IMAGE_PATH,
            'full_name': 'John Doe',
            'party': None,  # Invalid, party cannot be empty
            'position': None,  # Invalid, position cannot be empty
            'total_votes': 10,
            'description': 'Candidate description',
            'status': 'active',
            'created_at': '2023-05-26T12:00:00',
        }

        serializer = CandidateSerializer(data=serializer_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors['party'][0],
            'Party cannot be empty.'
        )
        self.assertEqual(
            serializer.errors['position'][0],
            'Position cannot be empty.'
        )
