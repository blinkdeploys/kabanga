# account/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
# from django.contrib.auth.views import LoginView
from .views import RegisterView #, LoginView
from .forms import UserAuthForm



urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path('login/', auth_views.LoginView.as_view(
        authentication_form=UserAuthForm,
    ), name='login'),

]
