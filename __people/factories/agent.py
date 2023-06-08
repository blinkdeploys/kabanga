import factory
from __people.models import Agent
from __poll.utils.factory_helpers import get_content_type
from __poll.constants import StatusChoices


class AgentFactory(factory.django.DjangoModelFactory):
    first_name = factory.Sequence(lambda n: f"Agent f{n}")
    last_name = factory.Sequence(lambda n: f"Agent l{n}")
    email = factory.Sequence(lambda n: f"email{n}@agent.gh")
    phone = factory.Sequence(lambda n: f"{n}{n}{n}{n}")
    zone_ct = None
    zone_id = None
    zone = None
    user = None
    status = StatusChoices.ACTIVE

    class Meta:
        model = Agent
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def create_with_zone(cls, zone_name='nation', *args, **kwargs):
        instance = cls.create(*args, **kwargs)
        instance.zone_ct, instance.zone_id, instance.zone = get_content_type(zone_name)
        instance.save()
        return instance
