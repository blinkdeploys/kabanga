import factory
from __geo.models import Nation

class NationFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: f'N-{n}')
    title = factory.Sequence(lambda n: f'Nation {n}')

    class Meta:
        model = Nation
