from rest_framework import serializers
from __poll.models import Position
from __geo.models import Station


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('pk', 'title', 'zone')

class PositionCollationSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    class Meta:
        model = Position
        fields = ('pk', 'title', 'zone', 'votes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_votes(self, obj):
        total = 0
        spk = self.context.get('spk')
        try:
            station = Station.objects.filter(pk=spk).first()
        except Exception as e:
            print('No station submitted.')
            pass
        # from pprint import pprint
        # pprint(self.context.get('request').__dict__)
        # pprint(spk)
        # pprint(station)
        # print(":::::::::::::::::::::::::::::::::::")
        for candidate in obj.candidates.all():
            if station is None:
                results = candidate.results.all()
            else:
                results = candidate.results \
                                   .filter(station=station) \
                                   .all()
            for result in results:
                total += result.votes
        return total

    # def get_votes(self, obj):
    #     from pprint import pprint
    #     print("...................")
    #     pprint(self.context.get('request'))
    #     # pprint(kwargs.get('context', None).get('request', None).__dict__)
    #     print(":::::::::::::::::::")
    #     return 0