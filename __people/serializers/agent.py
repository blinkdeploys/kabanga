from rest_framework import serializers
from __people.models import Agent
from __poll.constants import StatusChoices


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ('pk', 'full_name', 'zone', 'zone_title', 'zone_type', 'email', 'phone', 'address', 'zone_ct', 'zone_id', 'status', 'created_at')


class AgentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ('pk', 'first_name', 'last_name', 'email', 'address',
                  'description', 'zone_ct_id', 'zone_id', 'status',
                  # 'user',
                 )
        extra_kwargs = dict(
                            first_name=dict(required=True),
                            last_name=dict(required=True),
                            email=dict(required=True),
                            address=dict(required=False, default=''),
                            zone_ct_id=dict(required=True),
                            zone_id=dict(required=True),
                            description=dict(required=False, default=''),
                            status=dict(required=False, default=StatusChoices.ACTIVE),
                           )

