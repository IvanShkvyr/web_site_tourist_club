from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import CharField, PasswordInput
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    username = CharField(min_length=3, max_length=25, required=True)
    password1 = CharField(max_length=25, required=True, widget=PasswordInput())
    password2 = CharField(max_length=25, required=True, widget=PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class LoginForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ['username', 'password']
