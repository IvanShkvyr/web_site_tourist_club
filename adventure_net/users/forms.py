"""
Module containing various forms for user registration, authentication, and profile management.

This module provides the following form classes:
- RegisterForm: Form for user registration.
- LoginForm: Form for user authentication.
- CategoryForm: Form for creating user positions categories.
- MembersForm: Form for managing user profile information.
- UpdateAccountInformationForm: Form for updating user account information.
- RecoverLoginForm: Form for recovering login information.
- ResetPasswordForm: Form for resetting user password.

Each form class is a subclass of Django's ModelForm or Form, tailored to specific data requirements
and validations.

Note: This module requires the following external packages: `datetime`, `django`,
     `phonenumber_field`.
"""

from datetime import datetime
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import CharField, PasswordInput, ModelForm, TextInput, ImageField,\
    DateField, EmailField, ModelMultipleChoiceField, SelectMultiple, SelectDateWidget,\
    Form

from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

from . import models

class RegisterForm(UserCreationForm):
    """
    Form for user registration.

    Inherits from Django's UserCreationForm and adds custom validation for username and password.

    Attributes:
        username (CharField): Field for entering the username.
        password1 (CharField): Field for entering the password.
        password2 (CharField): Field for confirming the password.

    Meta:
        model (User): The User model.
        fields (list): The fields included in the form.

    Example:
        form = RegisterForm()
    """

    username = CharField(min_length=3, max_length=25, required=True)
    password1 = CharField(max_length=25, required=True, widget=PasswordInput())
    password2 = CharField(max_length=25, required=True, widget=PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    """
    Form for user authentication.

    Inherits from Django's AuthenticationForm.

    Meta:
        model (User): The User model.
        fields (list): The fields included in the form.

    Example:
        form = LoginForm()
    """

    class Meta:
        model = User
        fields = ['username', 'password']


class CategoryForm(ModelForm):
    """
    Form for creating user positions categories.

    Inherits from Django's ModelForm and adds custom validation for positions category.

    Attributes:
        positions_category (CharField): Field for entering the positions category.
        positions_category_info (CharField): Field for entering additional information
            about the category.

    Meta:
        model (UserPositions): The UserPositions model.
        fields (list): The fields included in the form.

    Methods:
        clean_positions_category: Cleans and formats the positions category field.

    Example:
        form = CategoryForm()
    """
    positions_category = CharField(min_length=3,
                                   max_length=20,
                                   required=True,
                                   widget=TextInput()
                                   )
    positions_category_info = CharField(
                                        min_length=15,
                                        max_length=150,
                                        required=True,
                                        widget=TextInput()
                                        )

    def clean_positions_category(self):
        positions_category = self.cleaned_data['positions_category']
        return positions_category.title()

    class Meta:
        model = models.UserPositions
        fields = ['positions_category', 'positions_category_info']

class MembersForm(ModelForm):
    """
    Form for managing user profile information.

    Inherits from Django's ModelForm and includes fields for various profile information.

    Attributes:
        user_name (CharField): Field for entering the user's first name.
        user_lastname (CharField): Field for entering the user's last name.
        user_birthday (DateField): Field for selecting the user's birthday.
        user_avatar (ImageField): Field for uploading the user's avatar image.
        user_position (ModelMultipleChoiceField): Field for selecting multiple user positions.
        user_experience (CharField): Field for entering the user's experience.
        user_location (CharField): Field for entering the user's location.
        user_info (CharField): Field for entering additional information about the user.
        phone (PhoneNumberField): Field for entering the user's phone number.

    Meta:
        model (Profile): The Profile model.
        fields (list): The fields included in the form.

    Example:
        form = MembersForm()
    """

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
    """
    Form for updating user account information.

    Inherits from Django's ModelForm and includes fields for username and password.

    Attributes:
        username (CharField): Field for entering the username.
        password (CharField): Field for entering the password.

    Meta:
        model (User): The User model.
        fields (list): The fields included in the form.

    Example:
        form = UpdateAccountInformationForm()
    """

    username = CharField(min_length=3, max_length=25, required=True)
    password = CharField(max_length=25, required=True, widget=PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'password']


class RecoverLoginForm(Form):
    """
    Form for recovering login information.

    Inherits from Django's Form and includes a field for entering the email address.

    Attributes:
        email (EmailField): Field for entering the email address.

    Example:
        form = RecoverLoginForm()
    """

    email = EmailField(label="Електронна адреса")


class ResetPasswordForm(Form):
    """
    Form for resetting user password.

    Inherits from Django's Form and includes a field for entering the new password.

    Attributes:
        password (CharField): Field for entering the new password.

    Example:
        form = ResetPasswordForm()
    """

    password = CharField(label='Новий пароль', widget=PasswordInput)
