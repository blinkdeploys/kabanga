from rest_framework import serializers
from __geo.models import Station
from __geo.serializers import ConstituencySerializer
from __geo.models import Station, Constituency, Region, Nation
from __people.models import Agent, Candidate
from __poll.utils.utils import get_zone_ct


class StationSubmitSerializer(serializers.ModelSerializer):
    constituency = ConstituencySerializer(read_only=True)
    class Meta:
        model = Station
        fields = ('code', 'title', 'constituency', 'status')

    def validate(self, attrs):
        for item in ['code', 'title', 'status']:
            attr = attrs.get(item)
            if not attr:
                raise serializers.ValidationError(f"{item} cannot be empty.")
        constituency = self.initial_data.get(f'constituency')
        if not (constituency and constituency['pk'] > 0):
            raise serializers.ValidationError(f"constituency cannot be empty.")
        attrs['constituency_id'] = constituency['pk']
        try:
            attrs['constituency'] = Constituency.objects.get(pk=attrs['constituency_id'])
        except Constituency.DoesNotExist:
            raise serializers.ValidationError(f"Constituency instance does not exits.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('constituency', None)
        instance = Station.objects.create(**validated_data)
        instance.save()
        return instance

    '''
    def to_internal_value(self, data):
        # Include the 'constituency_id' field in the 'attrs' dictionary
        if 'constituency_id' in data:
            data['constituency_id'] = self.fields['constituency_id'].to_internal_value(data['constituency_id'])
        return super().to_internal_value(data)
    '''


class StationSerializer(serializers.ModelSerializer):
    constituency = ConstituencySerializer()
    agent = serializers.SerializerMethodField()
    has_presidential_approval = serializers.SerializerMethodField()
    has_parliamentary_approval = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()
    total_presidential_votes = serializers.SerializerMethodField()
    total_parliamentary_votes = serializers.SerializerMethodField()

    class Meta:
        model = Station
        fields = ('pk', 'code', 'title', 'details', 'constituency', 'agent',
                  'total_votes', 'total_presidential_votes', 'total_parliamentary_votes', 'has_presidential_approval', 'has_parliamentary_approval',
                  'status', 'created_at')

    def get_total_votes(self, obj):
        total_votes = 0
        for result_sheet in obj.result_sheets.all():
            total_votes += result_sheet.total_valid_votes
        return total_votes

    def get_total_presidential_votes(self, obj):
        total_votes = 0
        for result_sheet in obj.result_sheets.all():
            if result_sheet.position.zone_ct == get_zone_ct(Nation):
                total_votes += result_sheet.total_valid_votes
        return total_votes

    def get_total_parliamentary_votes(self, obj):
        total_votes = 0
        for result_sheet in obj.result_sheets.all():
            if result_sheet.position.zone_ct == get_zone_ct(Constituency):
                total_votes += result_sheet.total_valid_votes
        return total_votes

    def get_has_presidential_approval(self, obj):
        nation_ct = get_zone_ct(Nation)
        constituency_ct = get_zone_ct(Constituency)
        region_ct = get_zone_ct(Region)
        station_ct = get_zone_ct(Station)
        ct = dict(station='1', constituency='1', region='1', nation='1')
        for result_sheet in obj.result_sheets.all():
            if result_sheet.position.zone_ct == nation_ct:
                for result_sheet_approval in result_sheet.approvals.all():
                    if result_sheet_approval.approving_agent.zone_ct == station_ct:
                        ct['station'] = ''
                    elif result_sheet_approval.approving_agent.zone_ct == constituency_ct:
                        ct['constituency'] = ''
                    elif result_sheet_approval.approving_agent.zone_ct == region_ct:
                        ct['region'] = ''
                    elif result_sheet_approval.approving_agent.zone_ct == nation_ct:
                        ct['nation'] = ''
        if ''.join(list(ct.values())) == '':
            return True
        return False

    def get_has_parliamentary_approval(self, obj):
        nation_ct = get_zone_ct(Nation)
        constituency_ct = get_zone_ct(Constituency)
        region_ct = get_zone_ct(Region)
        station_ct = get_zone_ct(Station)
        ct = dict(station='1', constituency='1', region='1', nation='1')
        for result_sheet in obj.result_sheets.all():
            if result_sheet.position.zone_ct == constituency_ct:
                for result_sheet_approval in result_sheet.approvals.all():
                    if result_sheet_approval.approving_agent.zone_ct == station_ct:
                        ct['station'] = ''
                    elif result_sheet_approval.approving_agent.zone_ct == constituency_ct:
                        ct['constituency'] = ''
                    elif result_sheet_approval.approving_agent.zone_ct == region_ct:
                        ct['region'] = ''
                    elif result_sheet_approval.approving_agent.zone_ct == nation_ct:
                        ct['nation'] = ''
        if ''.join(ct.values()) == '':
            return True
        return False

    def get_agent(self, obj):
        zone_ct = get_zone_ct(Station)
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


class StationCollationSerializer(StationSerializer):
    constituency = ConstituencySerializer()
    agent = serializers.SerializerMethodField()
    votes = serializers.SerializerMethodField()

    class Meta:
        model = Station
        fields = ('pk', 'code', 'title', 'votes', 'constituency', 'agent', 'status', 'created_at')

    def get_votes(self, obj):
        total = 0
        for result in obj.results.all():
            try:
                candidate = Candidate.objects.filter(pk=result.candidate.pk).first()
                total += result.votes
            except Exception as e:
                print(e)
        return total


class StationChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ('pk', 'code', 'title')
