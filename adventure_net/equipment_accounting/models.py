"""
This module contains the models for equipment management.

The models defined in this module represent the equipment categories, equipment,
and equipment bookings.

Classes:
- EquipmentsCategories: Represents the categories of equipment.
- Equipments: Represents the equipment.
- EquipmentBooking: Represents the booking of equipment.

"""
# pylint: disable=invalid-str-returned
# pylint: disable=E1101

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from PIL import Image


class EquipmentsCategories(models.Model):
    """
    Represents the categories of equipment.

    Attributes:
        equipment_category_name (CharField): The name of the equipment category.

    Methods:
        __str__: Returns the string representation of the equipment category.

    """
    equipment_category_name = models.CharField(max_length=20, unique=True, null=False)

    def __str__(self):
        return self.equipment_category_name


class Equipments(models.Model):
    """
    Represents the equipment.

    Attributes:
        equipment_name (CharField): The name of the equipment.
        equipment_category (ManyToManyField): The categories of the equipment.
        weight_of_equipment_kg (FloatField): The weight of the equipment in kilograms.
        photo_of_equipment (ImageField): The photo of the equipment.
        current_user (ForeignKey): The current user assigned to the equipment.
        equipment_description (CharField): The description of the equipment.

    Methods:
        __str__: Returns the string representation of the equipment.
        save: Overrides the save method to resize and save the photo of the equipment.

    """
    equipment_name = models.CharField(max_length=50, null=False)
    equipment_category = models.ManyToManyField(EquipmentsCategories)
    weight_of_equipment_kg = models.FloatField(null=False)
    photo_of_equipment = models.ImageField(default='default_tool.png', upload_to='equipment_images')
    current_user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    equipment_description = models.CharField(max_length=150, default="-")

    def __str__(self):
        return self.equipment_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        pic = Image.open(self.photo_of_equipment.path)

        if pic.height > 225 or pic.width > 225:
            pic.thumbnail((225, 225))

        square_image = Image.new('RGB', (225, 225), (255, 255, 255))
        square_image.paste(pic, ((225 - pic.size[0]) // 2, (225 - pic.size[1]) // 2))
        square_image.save(self.photo_of_equipment.path)




class EquipmentBooking(models.Model):
    """
    Represents the booking of equipment.

    Attributes:
        club_member (ForeignKey): The club member making the booking.
        reserved_equipment (ForeignKey): The equipment being reserved.
        booking_date_from (DateField): The start date of the booking.
        booking_date_to (DateField): The end date of the booking.

    Methods:
        __str__: Returns the string representation of the club member.

    """
    club_member = models.ForeignKey(User, on_delete=models.CASCADE)
    reserved_equipment = models.ForeignKey(Equipments, on_delete=models.CASCADE)
    booking_date_from = models.DateField()
    booking_date_to = models.DateField(default=timezone.now)

    def __str__(self):
        return self.club_member
