# account/urls.py
# from django.urls import path
from django.conf.urls import url
from __people.api import views as people_api_views


urlpatterns = [
    url(r'^agents/$', people_api_views.agent_list),
    url(r'^agent/(?P<pk>[0-9]+)$', people_api_views.agent_detail),
    url(r'^candidates/$', people_api_views.candidate_list),
    url(r'^candidate/(?P<pk>[0-9]+)$', people_api_views.candidate_detail),
    url(r'^parties/$', people_api_views.party_list),
    url(r'^party/(?P<pk>[0-9]+)$', people_api_views.party_detail),
]
