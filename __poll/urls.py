# account/urls.py
# from django.urls import path
from django.conf.urls import url
from __poll import views as poll_views


urlpatterns = [

    url(r'^events/$', poll_views.event_list, name="event_list"),
    url(r'^event/$', poll_views.event_detail, name="event_detail"),
    url(r'^event/(?P<pk>[0-9]+)$', poll_views.event_detail, name="event_detail"),
    url(r'^offices/$', poll_views.office_list, name="office_list"),
    url(r'^office/$', poll_views.office_detail, name="office_detail"),
    url(r'^office/(?P<pk>[0-9]+)$', poll_views.office_detail, name="office_detail"),
    url(r'^positions/$', poll_views.position_list, name="position_list"),
    # url(r'^position/$', poll_views.position_detail, name="position_detail"),
    url(r'^position/(?P<pk>[0-9]+)$', poll_views.position_detail, name="position_detail"),

    url(r'^result/$', poll_views.result_detail, name="result_detail"),
    url(r'^result/(?P<pk>[0-9]+)$', poll_views.result_detail, name="result_detail"),
    url(r'^results/$', poll_views.result_list, name="result_list"),
    url(r'^result/stations/$', poll_views.result_station_list, name="result_station_list"),
    url(r'^result/station/(?P<spk>[0-9]+)$', poll_views.result_position_list, name="result_position_list"),
    url(r'^result/station/(?P<spk>[0-9]+)/position/(?P<ppk>[0-9]+)$', poll_views.result_candidate_list, name="result_candidate_list"),


    url(r'^result_approvals/$', poll_views.result_approval_list, name="result_approval_list"),


    url(r'^result_approvals/presidential/$', poll_views.result_approval_list_presidential, name="result_approval_list_presidential"),
    url(r'^result_approvals/presidential/constituency/$', poll_views.result_approval_list_presidential_constituency, name="result_approval_list_presidential_constituency"),
    url(r'^result_approvals/presidential/region/$', poll_views.result_approval_list_presidential_regional, name="result_approval_list_presidential_regional"),
    url(r'^result_approvals/presidential/nation/$', poll_views.result_approval_list_presidential_national, name="result_approval_list_presidential_national"),
    url(r'^result_approvals/presidential/constituency/(?P<pk>[0-9]+)$', poll_views.result_approval_list_presidential_constituency, name="result_approval_list_presidential_constituency"),
    url(r'^result_approvals/presidential/region/(?P<pk>[0-9]+)$', poll_views.result_approval_list_presidential_regional, name="result_approval_list_presidential_regional"),
    url(r'^result_approvals/presidential/nation/(?P<pk>[0-9]+)$', poll_views.result_approval_list_presidential_national, name="result_approval_list_presidential_national"),

    url(r'^result_approvals/parliamentary/$', poll_views.result_approval_list_parliamentary, name="result_approval_list_parliamentary"),
    url(r'^result_approvals/parliamentary/constituency/$', poll_views.result_approval_list_parliamentary_constituency, name="result_approval_list_parliamentary_constituency"),
    url(r'^result_approvals/parliamentary/region/$', poll_views.result_approval_list_parliamentary_regional, name="result_approval_list_parliamentary_regional"),
    url(r'^result_approvals/parliamentary/nation/$', poll_views.result_approval_list_parliamentary_national, name="result_approval_list_parliamentary_national"),
    url(r'^result_approvals/parliamentary/constituency/(?P<pk>[0-9]+)$', poll_views.result_approval_list_parliamentary_constituency, name="result_approval_list_parliamentary_constituency"),
    url(r'^result_approvals/parliamentary/region/(?P<pk>[0-9]+)$', poll_views.result_approval_list_parliamentary_regional, name="result_approval_list_parliamentary_regional"),
    url(r'^result_approvals/parliamentary/nation/(?P<pk>[0-9]+)$', poll_views.result_approval_list_parliamentary_national, name="result_approval_list_parliamentary_national"),


    url(r'^approve/presidential/$', poll_views.result_approval_list_presidential, name="approve_presidential"),
    url(r'^approve/presidential/constituency/$', poll_views.result_approval_list_presidential_constituency, name="approve_presidential_constituency"),
    url(r'^approve/presidential/region/$', poll_views.result_approval_list_presidential_regional, name="approve_presidential_regional"),
    url(r'^approve/presidential/nation/$', poll_views.result_approval_list_presidential_national, name="approve_presidential_national"),
    url(r'^approve/presidential/constituency/(?P<pk>[0-9]+)$', poll_views.approve_presidential_constituency, name="approve_presidential_constituency"),
    url(r'^approve/presidential/region/(?P<pk>[0-9]+)$', poll_views.approve_presidential_regional, name="approve_presidential_regional"),
    url(r'^approve/presidential/nation/(?P<pk>[0-9]+)$', poll_views.approve_presidential_national, name="approve_presidential_national"),

    url(r'^approve/parliamentary/$', poll_views.result_approval_list_parliamentary, name="approve_parliamentary"),
    url(r'^approve/parliamentary/constituency/$', poll_views.result_approval_list_parliamentary_constituency, name="approve_parliamentary_constituency"),
    url(r'^approve/parliamentary/region/$', poll_views.result_approval_list_parliamentary_regional, name="approve_parliamentary_regional"),
    url(r'^approve/parliamentary/nation/$', poll_views.result_approval_list_parliamentary_national, name="approve_parliamentary_national"),
    url(r'^approve/parliamentary/constituency/(?P<pk>[0-9]+)$', poll_views.approve_parliamentary_constituency, name="approve_parliamentary_constituency"),
    url(r'^approve/parliamentary/region/(?P<pk>[0-9]+)$', poll_views.approve_parliamentary_regional, name="approve_parliamentary_regional"),
    url(r'^approve/parliamentary/nation/(?P<pk>[0-9]+)$', poll_views.approve_parliamentary_national, name="approve_parliamentary_national"),


    url(r'^result_approval/$', poll_views.result_approval_detail, name="result_approval_detail"),
    url(r'^result_approval/(?P<pk>[0-9]+)$', poll_views.result_approval_detail, name="result_approval_detail"),
    url(r'^approval/station/(?P<spk>[0-9]+)/position/(?P<ppk>[0-9]+)$', poll_views.result_approval_form, name="result_approval_form"),

]
