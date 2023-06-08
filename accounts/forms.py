# users/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from account.models import User
from django.forms.widgets import PasswordInput, TextInput


class UserAuthForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={
                                            'class': 'form-control',
                                            'placeholder': 'enter username',
                                        }))
    password = forms.CharField(widget=PasswordInput(attrs={
                                            'class': 'form-control',
                                            'type': 'password',
                                            'placeholder':'enter password',
                                        }))


class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'email')


class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email')
