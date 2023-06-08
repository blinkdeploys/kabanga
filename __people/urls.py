# account/urls.py
# from django.urls import path
from django.conf.urls import url
from __people import views as people_views


urlpatterns = [

    # url(r'^api/agents/$', people_views.agent_list),
    # url(r'^api/agent/(?P<pk>[0-9]+)$', people_views.agent_detail),
    # url(r'^api/candidates/$', people_views.candidate_list),
    # url(r'^api/candidate/(?P<pk>[0-9]+)$', people_views.candidate_detail),
    # url(r'^api/parties/$', people_views.party_list),
    # url(r'^api/party/(?P<pk>[0-9]+)$', people_views.party_detail),

    url(r'^agents/$', people_views.agent_list, name="agent_list"),
    url(r'^agents/(?P<q>[.]+)$', people_views.agent_list, name="agent_list"),
    url(r'^agent/$', people_views.agent_detail, name="agent_detail"),
    url(r'^agent/(?P<pk>[0-9]+)$', people_views.agent_detail, name="agent_detail"),
    url(r'^parties/$', people_views.party_list, name="party_list"),
    url(r'^parties/(?P<q>[.]+)$', people_views.party_list, name="party_list"),
    url(r'^party/$', people_views.party_detail, name="party_detail"),
    url(r'^party/(?P<pk>[0-9]+)$', people_views.party_detail, name="party_detail"),
    url(r'^candidates/$', people_views.candidate_list, name="candidate_list"),
    url(r'^candidates/(?P<q>[.]+)$', people_views.candidate_list, name="candidate_list"),
    url(r'^candidate/$', people_views.candidate_detail, name="candidate_detail"),
    url(r'^candidate/(?P<pk>[0-9]+)$', people_views.candidate_detail, name="candidate_detail"),

]
