from django.apps import apps
from __poll.utils.utils import get_zone_ct
from __geo.factories import NationFactory, RegionFactory, ConstituencyFactory, StationFactory


def get_content_type(zone_name):
    if zone_name == 'nation':
        instance = NationFactory()
        model = apps.get_model('__geo', zone_name)
        return get_zone_ct(model), instance.pk, instance
    elif zone_name == 'region':
        nation = NationFactory()
        instance = RegionFactory(nation=nation)
        model = apps.get_model('__geo', zone_name)
        return get_zone_ct(model), instance.pk, instance
    elif zone_name == 'constituency':
        nation = NationFactory()
        region = RegionFactory(nation=nation)
        instance = ConstituencyFactory(region=region)
        model = apps.get_model('__geo', zone_name)
        return get_zone_ct(model), instance.pk, instance
    elif zone_name == 'station':
        nation = NationFactory()
        region = RegionFactory(nation=nation)
        constituency = ConstituencyFactory(region=region)
        instance = StationFactory(constituency=constituency)
        model = apps.get_model('__geo', zone_name)
        return get_zone_ct(model), instance.pk, instance
    return None, None, None
