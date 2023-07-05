"""
This module contains the models for users management.

The models defined in this module represent the user positions, users,
and token.

Classes:
- UserPositions: Represents the type of users.
- Profile: Represents the info about users.
- RecoveryToken: Represents the storege for tokens.

"""
# pylint: disable=invalid-str-returned
# pylint: disable=E1101

from django.contrib.auth.models import User
from django.db import models

from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField


class UserPositions(models.Model):
    """
    Represents the type of users.

    Attributes:
        positions_category (CharField): The name of the position category.
        positions_category_info (CharField): The discription of the position category.

    Methods:
        __str__: Returns the string representation of the position category.

    """

    positions_category = models.CharField(max_length=20, unique=True, null=False)
    positions_category_info = models.CharField(max_length=150)

    def __str__(self):
        return self.positions_category


class Profile(models.Model):
    """
    Represents a user profile.

    This model stores information about a user's profile, including their name, lastname,
    birthday, avatar, position, experience, location, contact information, and associated
    user account.

    Attributes:
        user_name (str): The user's first name.
        user_lastname (str): The user's last name.
        user_birthday (datetime.date, optional): The user's birthday (can be blank or null).
        user_avatar (django.db.models.ImageField): The user's avatar image
            (default: 'avatar_default.png').
        user_position (django.db.models.ManyToManyField): Many-to-many relationship with
            UserPositions model.
        user_experience (str): Information about the user's experience.
        user_location (str): The user's location.
        user_info (str): Additional information about the user.
        phone (phonenumber_field.modelfields.PhoneNumberField, optional): The user's phone
            number (can be blank).
        email (django.db.models.EmailField): The user's email address.
        user (django.db.models.OneToOneField): One-to-one relationship with the User model.

    Methods:
        __str__(): Returns a string representation of the profile.
        save(*args, **kwargs): Overrides the save method to perform additional actions after
            saving the profile.
    """

    user_name = models.CharField(max_length=50)
    user_lastname = models.CharField(max_length=50)
    user_birthday = models.DateField(blank=True, null=True)
    user_avatar = models.ImageField(default='avatar_default.png', upload_to='profile_images')
    user_position = models.ManyToManyField(UserPositions)
    user_experience = models.CharField(max_length=250)
    user_location = models.CharField(max_length=50)
    user_info = models.CharField(max_length=250)
    phone = PhoneNumberField(blank=True)
    email = models.EmailField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        """
        Overrides the save method to perform additional actions after saving the profile.

        This method is called when saving the profile instance. It resizes and crops the
        user's avatar image to a square of 225x225 pixels, maintaining the aspect ratio.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        super().save(*args, **kwargs)

        pic = Image.open(self.user_avatar.path)

        if pic.height > 225 or pic.width > 225:
            pic.thumbnail((225, 225))

        square_image = Image.new('RGB', (225, 225), (255, 255, 255))
        square_image.paste(pic, ((225 - pic.size[0]) // 2, (225 - pic.size[1]) // 2))
        square_image.save(self.user_avatar.path)


class RecoveryToken(models.Model):
    """
    Model representing a recovery token for resetting user's password.

    This model stores the recovery token generated for a user to reset their password.
    It contains fields for the token itself, the associated user, and the creation timestamp.

    Attributes:
        token (str): The recovery token string.
        user (ForeignKey): The associated User object.
        created_at (DateTimeField): The timestamp of token creation.

    Methods:
        __str__: Returns the string representation of the token.

    """

    token = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
