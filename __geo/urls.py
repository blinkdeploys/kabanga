# account/urls.py
# from django.urls import path
from django.conf.urls import url
from __geo import views as geo_views


urlpatterns = [
    url(r'^$', geo_views.home_view, name="geo_home"),
    url(r'^nations/$', geo_views.nation_list, name="nation_list"),
    url(r'^nations/(?P<q>[.]+)$', geo_views.nation_list, name="nation_item"),
    url(r'^nation/$', geo_views.nation_detail, name="nation_detail"),
    url(r'^nation/(?P<pk>[0-9]+)$', geo_views.nation_detail, name="nation_detail"),
    url(r'^regions/$', geo_views.region_list, name="region_list"),
    url(r'^regions/(?P<q>[.]+)$', geo_views.region_list, name="region_item"),
    url(r'^region/$', geo_views.region_detail, name="region_detail"),
    url(r'^region/(?P<pk>[0-9]+)$', geo_views.region_detail, name="region_detail"),
    url(r'^constituencies/$', geo_views.constituency_list, name="constituency_list"),
    url(r'^constituencies/(?P<q>[.]+)$', geo_views.constituency_list, name="constituency_item"),
    url(r'^constituency/$', geo_views.constituency_detail, name="constituency_detail"),
    url(r'^constituency/(?P<pk>[0-9]+)$', geo_views.constituency_detail, name="constituency_detail"),
    url(r'^stations/$', geo_views.station_list, name="station_list"),
    url(r'^stations/(?P<q>[.]+)$', geo_views.station_list, name="station_item"),
    url(r'^station/$', geo_views.station_detail, name="station_detail"),
    url(r'^station/(?P<pk>[0-9]+)$', geo_views.station_detail, name="station_detail"),

]
