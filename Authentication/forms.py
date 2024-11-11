from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.forms.widgets import PasswordInput, TextInput

from .models import Role, User

class CreateUser(UserCreationForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all())
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role']

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())