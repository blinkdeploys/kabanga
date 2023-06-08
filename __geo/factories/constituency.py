import factory
from __geo.models import Constituency

class ConstituencyFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: f'Constituency {n}')
    region = factory.SubFactory('__geo.factories.RegionFactory')

    class Meta:
        model = Constituency