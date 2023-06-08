import factory
from __geo.models import Station

class StationFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: f'Station {n}')
    code = factory.Sequence(lambda n: f'CODE{n}')
    constituency = factory.SubFactory('__geo.factories.ConstituencyFactory')

    class Meta:
        model = Station