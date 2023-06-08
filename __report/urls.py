from django.conf.urls import url
from __report import views as report_views
from __report.api import views as api_views


urlpatterns = [
    url(r'^$', report_views.index_view, name='report_home'),

    url(r'^clear/$', api_views.clear_collation, name="clear-results"),
    url(r'^enqueue/$', api_views.enqueue_collation, name="enqueue"),
    url(r'^dequeue/(?P<jid>rq:job:[0-9a-zA-Z]+-[0-9a-zA-Z]+-[0-9a-zA-Z]+-[0-9a-zA-Z]+-[0-9a-zA-Z]+)$', api_views.dequeue_collation, name="dequeue"),

    url(r'^collate/items$', api_views.manage_items, name="items"),
    url(r'^collate/items/<slug:key>$', api_views.manage_item, name="single_item"),

    url(r'^presidential/nation/$', report_views.nation_presidential_report, name="nation_presidential_report"),
    url(r'^presidential/nation/(?P<npk>[0-9]+)$', report_views.nation_presidential_report, name="nation_presidential_report"),
    url(r'^presidential/region/(?P<rpk>[0-9]+)$', report_views.region_presidential_report, name="region_presidential_report"),
    url(r'^presidential/constituency/(?P<cpk>[0-9]+)$', report_views.constituency_presidential_report, name="constituency_presidential_report"),
    url(r'^presidential/station/(?P<spk>[0-9]+)$', report_views.station_presidential_report, name="station_presidential_report"),

    url(r'^parliamentary/nation/$', report_views.nation_parliamentary_report, name="nation_parliamentary_report"),
    url(r'^parliamentary/nation/(?P<npk>[0-9]+)$', report_views.nation_parliamentary_report, name="nation_parliamentary_report"),
    url(r'^parliamentary/region/(?P<rpk>[0-9]+)$', report_views.region_parliamentary_report, name="region_parliamentary_report"),
    url(r'^parliamentary/constituency/(?P<cpk>[0-9]+)$', report_views.constituency_parliamentary_report, name="constituency_parliamentary_report"),
    url(r'^parliamentary/station/(?P<spk>[0-9]+)$', report_views.station_parliamentary_report, name="station_parliamentary_report"),


    url(r'^presidential/wins/nation$', report_views.presidential_win_report, name="presidential_win_nation_report"),
    url(r'^presidential/wins/region$', report_views.presidential_win_report, name="presidential_win_region_report"),
    url(r'^presidential/wins/constituency$', report_views.presidential_win_report, name="presidential_win_constituency_report"),
    url(r'^presidential/wins/station$', report_views.presidential_win_report, name="presidential_win_station_report"),
    url(r'^presidential/wins/$', report_views.presidential_win_report, name="presidential_win_report"),

    url(r'^parliamentary/seats/$', report_views.parliamentary_seat_report, name="parliamentary_seat_report"),
    url(r'^parliamentary/seats/(?P<pk>[0-9]+)$', report_views.parliamentary_seat_report, name="parliamentary_seat_party_report"),


    url(r'^dashboard/$', report_views.dashboard, name="dashboard"),
    url(r'^dashboard/map/$', report_views.dash_map, name="dash_map"),

    url(r'^api/demo_dash/$', api_views.demo_dash, name="api_demo_dash"),
    url(r'^api/dashboard/$', api_views.dashboard, name="api_dashboard"),
]
