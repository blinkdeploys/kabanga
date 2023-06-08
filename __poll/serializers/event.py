from rest_framework import serializers
from __poll.models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('pk', 'title', 'details', 'level', 'position', 'start', 'end', 'status', 'created_at')
