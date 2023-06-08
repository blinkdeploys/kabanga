from rest_framework import serializers
from __geo.serializers import NationSerializer
from __geo.models import Nation, Region, Constituency
from __people.models import Agent
from __poll.utils.utils import get_zone_ct


class RegionSubmitSerializer(serializers.ModelSerializer):
    nation = NationSerializer(read_only=True)
    class Meta:
        model = Region
        fields = ('title', 'nation', 'status')

    def validate(self, attrs):
        for item in ['title', 'status']:
            attr = attrs.get(item)
            if not attr:
                raise serializers.ValidationError(f"{item} cannot be empty.")
        nation = self.initial_data.get(f'nation')
        if not (nation and nation['pk'] > 0):
            raise serializers.ValidationError(f"nation cannot be empty.")
        attrs['nation_id'] = nation['pk']
        try:
            attrs['nation'] = Nation.objects.get(pk=attrs['nation_id'])
        except Nation.DoesNotExist:
            raise serializers.ValidationError(f"Nation instance does not exits.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('nation', None)
        instance = Region.objects.create(**validated_data)
        instance.save()
        return instance


class RegionSerializer(serializers.ModelSerializer):
    nation = NationSerializer()
    agent = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()
    total_parliamentary_votes = serializers.SerializerMethodField()
    total_presidential_votes = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ('pk', 'title', 'details', 'nation', 'agent',
                  'total_votes',
                  'total_presidential_votes',
                  'total_parliamentary_votes',
                  'status', 'created_at')

    def get_total_votes(self, obj):
        votes = 0
        sheets = obj.national_collation_sheets.all()
        for sheet in sheets:
            votes = votes + int(sheet.total_votes)
        return votes

    def get_total_parliamentary_votes(self, obj):
        votes = 0
        sheets = obj.national_collation_sheets \
                    .filter(
                        zone_ct=get_zone_ct(Constituency)
                    ).all()
        for sheet in sheets:
            votes = votes + int(sheet.total_votes)
        return votes

    def get_total_presidential_votes(self, obj):
        votes = 0
        sheets = obj.national_collation_sheets \
                    .filter(
                        zone_ct=get_zone_ct(Nation)
                    ).all()
        for sheet in sheets:
            votes = votes + int(sheet.total_votes)
        return votes

    def get_agent(self, obj):
        zone_ct = get_zone_ct(Region)
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


class RegionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('pk', 'title')
