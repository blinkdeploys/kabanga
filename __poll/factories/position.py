import factory
from __poll.models import Position
from __poll.utils.factory_helpers import get_content_type


class PositionFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Position f{n}")
    details = factory.Sequence(lambda n: f"Position details l{n}")
    zone_ct = None
    zone_id = None
    zone = None

    class Meta:
        model = Position

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def create_with_zone(cls, zone_name='nation', *args, **kwargs):
        instance = cls.create(*args, **kwargs)
        instance.zone_ct, instance.zone_id, instance.zone = get_content_type(zone_name)
        instance.save()
        return instance
