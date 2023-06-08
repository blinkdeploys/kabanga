import factory
from __geo.models import Region, Nation

class RegionFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: f'Region {n}')
    nation = factory.SubFactory('__geo.factories.NationFactory')

    class Meta:
        model = Region