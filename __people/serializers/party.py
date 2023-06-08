from rest_framework import serializers
from __people.models import Party


class PartyAsChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ('pk', 'code', 'title', 'agent', 'status',
                  'result_votes', 'total_presidential_votes', 'total_parliamentary_votes',
                  )

class PartySerializer(serializers.ModelSerializer):
    # result_votes = serializers.SerializerMethodField()
    # candidates = serializers.SerializerMethodField()
    # total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Party
        fields = ('pk', 'code', 'title', 'details',
                  'total_candidates',
                  'candidates',
                  'result_votes', 'total_presidential_votes', 'total_parliamentary_votes',
                  'agent', 'status', 'created_at')

    # def get_total_votes(self, obj):
    #     total_votes = 0
    #     for candidate in obj.candidates.all():
    #         for result in candidate.results.all():
    #             total_votes += result.votes
    #     return total_votes

    # def get_candidates(self, obj):
    #     return obj.candidate_set.all()
