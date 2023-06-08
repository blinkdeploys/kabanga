# account/urls.py
# from django.urls import path
from django.conf.urls import url
from .views import nation, region, constituency, station


urlpatterns = [
    url(r'^nations/$', nation.nation_list, name="api_nation_list"),
    url(r'^nation/$', nation.nation_post, name="api_nation_post"),
    url(r'^nation/(?P<pk>[0-9]+)$', nation.nation_detail, name="api_nation_detail"),
    url(r'^regions/$', region.region_list, name="api_region_list"),
    url(r'^region/$', region.region_post, name="api_region_post"),
    url(r'^region/(?P<pk>[0-9]+)$', region.region_detail, name="api_region_detail"),
    url(r'^constituencies/$', constituency.constituency_list, name="api_constituency_list"),
    url(r'^constituency/$', constituency.constituency_post, name="api_constituency_post"),
    url(r'^constituency/(?P<pk>[0-9]+)$', constituency.constituency_detail, name="api_constituency_detail"),
    url(r'^stations/$', station.station_list, name="api_station_list"),
    url(r'^station/$', station.station_post, name="api_station_post"),
    url(r'^station/(?P<pk>[0-9]+)$', station.station_detail, name="api_station_detail"),

    url(r'^nation/choices/$', nation.nation_choices, name="nation_choices"),
    url(r'^region/choices/$', region.region_choices, name="region_choices"),
    url(r'^constituency/choices/$', constituency.constituency_choices, name="constituency_choices"),
    url(r'^station/choices/$', station.station_choices, name="station_choices"),
]
