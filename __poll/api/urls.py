# account/urls.py
# from django.urls import path
from django.conf.urls import url
from __poll import views as poll_views
# from .views import RegisterView


urlpatterns = [
    # path("register/", RegisterView.as_view(), name="register"),
    url(r'^events/$', poll_views.event_list),
    url(r'^event/(?P<pk>[0-9]+)$', poll_views.event_detail),
    url(r'^offices/$', poll_views.office_list),
    url(r'^office/(?P<pk>[0-9]+)$', poll_views.office_detail),
    url(r'^positions/$', poll_views.position_list),
    url(r'^position/(?P<pk>[0-9]+)$', poll_views.position_detail),
    url(r'^results/$', poll_views.result_list),
    url(r'^result/(?P<pk>[0-9]+)$', poll_views.result_detail),
    url(r'^result_approvals/$', poll_views.result_approval_list),
    url(r'^result_approval/(?P<pk>[0-9]+)$', poll_views.result_approval_detail),
]
