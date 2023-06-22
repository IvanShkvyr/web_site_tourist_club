from datetime import datetime
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import CharField, PasswordInput, ModelForm, TextInput, ImageField,\
DateField, EmailField, ModelMultipleChoiceField, SelectMultiple, SelectDateWidget

from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

from . import models

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


class CategoryForm(ModelForm):
    positions_category = CharField(min_length=3, max_length=20, required=True, widget=TextInput())
    positions_category_info = CharField(min_length=15, max_length=150, required=True, widget=TextInput())

    class Meta:
        model = models.UserPositions
        fields = ['positions_category', 'positions_category_info']

class MembersForm(ModelForm):
    user_name = CharField(max_length=50, required=True, widget=TextInput())
    user_lastname = CharField(max_length=50, required=True, widget=TextInput())
    user_birthday = DateField(required=False, widget=SelectDateWidget(
            years=range(1950, datetime.today().year)
        ))
    user_avatar = ImageField(required=False)
    user_position = ModelMultipleChoiceField(
        queryset=models.UserPositions.objects.all(),
        widget=SelectMultiple,
        required=False
    )
    user_experience = CharField(max_length=250, required=False, widget=TextInput())
    user_location = CharField(max_length=50, required=False, widget=TextInput())
    user_info = CharField(max_length=250, required=False, widget=TextInput())
    phone = PhoneNumberField()

    class Meta:
        model = models.Profile
        fields = [
            'user_name',
            'user_lastname',
            'user_birthday',
            'user_avatar',
            'user_position',
            'user_experience',
            'user_location',
            'user_info',
            'phone',
            'email',
        ]


class UpdateAccountInformationForm(ModelForm):
    username = CharField(min_length=3, max_length=25, required=True)
    password = CharField(max_length=25, required=True, widget=PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'password']