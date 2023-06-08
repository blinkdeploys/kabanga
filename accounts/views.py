# from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from .forms import UserAuthForm, UserCreationForm
from django.contrib.auth.views import LoginView


class LoginView(LoginView):
    form_class = UserAuthForm
    # authentication_form=UserLoginForm
    success_url = reverse_lazy("home")
    template_name = "registration/login.html"

    def form_valid(self, form):
        # checkbox = form.cleaned_data['required_checkbox']
        # print(checkbox)
        return super().form_valid(form)


class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"
