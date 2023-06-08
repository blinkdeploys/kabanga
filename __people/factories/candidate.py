import factory
from django.apps import apps
from __people.models import Candidate
from __poll.factories import PositionFactory
from __poll.constants import StatusChoices


class CandidateFactory(factory.django.DjangoModelFactory):
    prefix = "M."
    first_name = factory.Sequence(lambda n: f"First f{n}")
    last_name = factory.Sequence(lambda n: f"Last l{n}")
    other_names = factory.Sequence(lambda n: f"Names l{n}")
    description = factory.Sequence(lambda n: f"Candidate details {n}")
    photo = ""
    party = None
    position = None
    status = StatusChoices.ACTIVE

    class Meta:
        model = Candidate

    def __init__(self, *args, **kwargs):
        position_name = kwargs.pop('position_name', None)
        super().__init__(*args, **kwargs)

        if self.position is None:
            if position_name:
                self.position = PositionFactory(position_name)

        party_model = apps.get_model('__people', 'party')
        if self.party is None:
            self.party = party_model(code='PAR', title='Party')
