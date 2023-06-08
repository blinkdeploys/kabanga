from rest_framework import serializers
from __geo.models import Constituency
from __geo.serializers import RegionSerializer
from __people.models import Agent
from __geo.models import Nation, Region, Constituency
from __poll.utils.utils import get_zone_ct


class ConstituencySubmitSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    class Meta:
        model = Constituency
        fields = ('title', 'region', 'status')

    def validate(self, attrs):
        for item in ['title', 'status']:
            attr = attrs.get(item)
            if not attr:
                raise serializers.ValidationError(f"{item} cannot be empty.")
        region = self.initial_data.get(f'region')
        if not (region and region['pk'] > 0):
            raise serializers.ValidationError(f"region cannot be empty.")
        attrs['region_id'] = region['pk']
        try:
            attrs['region'] = Region.objects.get(pk=attrs['region_id'])
        except Region.DoesNotExist:
            raise serializers.ValidationError(f"Region instance does not exits.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('region', None)
        instance = Constituency.objects.create(**validated_data)
        instance.save()
        return instance


class ConstituencySerializer(serializers.ModelSerializer):
    region = RegionSerializer()
    agent = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()
    total_parliamentary_votes = serializers.SerializerMethodField()
    total_presidential_votes = serializers.SerializerMethodField()

    class Meta:
        model = Constituency
        fields = ('pk', 'title', 'region',
                  'total_votes', 'total_presidential_votes', 'total_parliamentary_votes',
                  'agent', 'status', 'created_at')

    def get_total_votes(self, obj):
        votes = 0
        sheets = obj.regional_collation_sheets.all()
        for sheet in sheets:
            votes = votes + int(sheet.total_votes)
        return votes

    def get_total_parliamentary_votes(self, obj):
        votes = 0
        sheets = obj.regional_collation_sheets \
                    .filter(
                        zone_ct=get_zone_ct(Constituency)
                    ).all()
        for sheet in sheets:
            votes = votes + int(sheet.total_votes)
        return votes

    def get_total_presidential_votes(self, obj):
        votes = 0
        sheets = obj.regional_collation_sheets \
                    .filter(
                        zone_ct=get_zone_ct(Nation)
                    ).all()
        for sheet in sheets:
            votes = votes + int(sheet.total_votes)
        return votes
    
    def get_agent(self, obj):
        zone_ct = get_zone_ct(Constituency)
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


class ConstituencyChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Constituency
        fields = ('pk', 'title')
