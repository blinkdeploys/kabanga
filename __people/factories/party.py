import factory
from django.apps import apps
from __people.models import Party
from __poll.constants import StatusChoices


class PartyFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: f"PTY{n}")
    title = factory.Sequence(lambda n: f"Party Title {n}")
    details = factory.Sequence(lambda n: f"Party details {n}")
    agent = factory.SubFactory('__people.factories.AgentFactory')
    status = StatusChoices.ACTIVE

    class Meta:
        model = Party

