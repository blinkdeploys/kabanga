from rest_framework import serializers
from __people.models import Candidate
from .party import PartyAsChildSerializer
from __poll.serializers import PositionSerializer
from django.apps import apps
from __poll.serializers.sub import FileUploadSerializer


class CandidateDetailSerializer(serializers.ModelSerializer):
    party = PartyAsChildSerializer()
    position = PositionSerializer()
    photo = serializers.SerializerMethodField(required=False)
    # photo = FileUploadSerializer(required=False)

    class Meta:
        model = Candidate
        fields = ('pk', 'photo', 'first_name', 'last_name', 'party', 'position', 'description', 'status')

    def get_photo(self, instance):
        return instance.photo.path if instance.photo else None

    '''
    def validate(self, attrs):
        for item in ['first_name', 'last_name', 'party', 'position']:
            attr = attrs.get(item.replace('_', ' ').capitalize())
            if not attr:
                raise serializers.ValidationError(f"{item} cannot be empty.")
        return attrs

    def validate(self, attrs):
        for item in ['first_name', 'last_name', 'party', 'position']:
            attr = attrs.get(item)
            if not attr:
                field_name = item.relace('_', ' ').capitalize()
                raise serializers.ValidationError(f"{field_name} cannot be empty.")
        required_instances = [('__poll', 'position'), ('__people', 'party')]
        for app, required in required_instances:
            required_instance = self.initial_data.get(required)
            instance_model = apps.get_model(app, required)
            if not (required_instance and required_instance['pk'] > 0):
                raise serializers.ValidationError(f"{required.capitalize()} cannot be empty.")
            attrs[f'{required}_id'] = required_instance['pk']
            try:
                attrs[required] = instance_model.objects.get(pk=attrs[f'{required}_id'])
            except instance_model.DoesNotExist:
                raise serializers.ValidationError(f"{required.capitalize()} instance does not exits.")
        return attrs
    '''


class CandidateSerializer(serializers.ModelSerializer):
    party = PartyAsChildSerializer()
    position = PositionSerializer()
    photo = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Candidate
        fields = ('pk', 'photo', 'full_name',
                  'party', 'position', 'total_votes',
                  'description', 'status', 'created_at')

    def get_photo(self, instance):
        return instance.photo.path if instance.photo else None

    def update(self, instance, validated_data):
        photo_path = validated_data.pop('photo', None)
        if photo_path:
            instance.photo = photo_path
        else:
            instance.photo = instance.photo
        instance.save()
        return instance


'''
class CandidateCollateSerializer(serializers.ModelSerializer):
    party = PartyAsChildSerializer()
    position = PositionSerializer()
    votes = PositionSerializer()
    class Meta:
        model = Candidate
        fields = ('pk', 'full_name', 'party', 'position', 'votes', 'status', 'created_at')
'''
