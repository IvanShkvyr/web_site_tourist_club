from django.contrib.auth.models import User
from django.db import models

from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField



class UserPositions(models.Model):
    positions_category = models.CharField(max_length=20, unique=True, null=False)
    positions_category_info = models.CharField(max_length=150)

    def __str__(self):
        return self.positions_category


class Profile(models.Model):
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
        super().save(*args, **kwargs)

        pic = Image.open(self.user_avatar.path)

        if pic.height > 225 or pic.width >225:
            pic.thumbnail((225, 225))
            pic.save()