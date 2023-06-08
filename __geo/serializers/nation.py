from rest_framework import serializers
from __geo.models import Nation, Constituency
from __people.models import Agent
from __people.serializers import AgentSerializer
from __poll.utils.utils import get_zone_ct


class NationSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nation
        fields = ('code', 'title',)

    def validate(self, attrs):
        for item in ['code', 'title',]:
            attr = attrs.get(item)
            if not attr:
                raise serializers.ValidationError(f"{item} cannot be empty.")
        return attrs

    def create(self, validated_data):
        if Nation.objects.count() > 0:
            raise serializers.ValidationError(f"Nation already exists. Only one record can exist.")
        instance = Nation.objects.create(**validated_data)
        instance.save()
        return instance
        


class NationSerializer(serializers.ModelSerializer):
    agent = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()
    total_parliamentary_votes = serializers.SerializerMethodField()
    total_presidential_votes = serializers.SerializerMethodField()

    class Meta:
        model = Nation
        fields = ('pk', 'code', 'title', 'agent',
                  'total_votes', 'total_parliamentary_votes', 'total_presidential_votes',
                #   'status', 'created_at'
                  )

    def get_total_votes(self, obj):
        votes = 0
        sheets = obj.supernational_collation_sheets.all()
        for sheet in sheets:
            votes = votes + int(sheet.total_votes)
        return votes

    def get_total_parliamentary_votes(self, obj):
        votes = 0
        sheets = obj.supernational_collation_sheets \
                    .filter(
                        zone_ct=get_zone_ct(Constituency)
                    ).all()
        for sheet in sheets:
            votes = votes + int(sheet.total_votes)
        return votes

    def get_total_presidential_votes(self, obj):
        votes = 0
        sheets = obj.supernational_collation_sheets \
                    .filter(
                        zone_ct=get_zone_ct(Nation)
                    ).all()
        for sheet in sheets:
            votes = votes + int(sheet.total_votes)
        return votes
    
    def get_agent(self, obj):
        zone_ct = get_zone_ct(Nation)
        agent = Agent.objects.filter(
                        zone_ct=zone_ct,
                        zone_id=obj.pk
                    ).first()
        if agent is not None:
            return dict(
                pk=agent.pk,
                full_name=agent.full_name,
                email=agent.email,
                phone=agent.phone,
                address=agent.address,
            )
        return None


class NationChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nation
        fields = ('pk', 'code', 'title')
