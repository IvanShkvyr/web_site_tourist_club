from django.db import models


class EquipmentsCategories(models.Model):
    equipment_category_name = models.CharField(max_length=20, unique=True, null=False)

    def __str__(self):
        return self.equipment_category_name


class Equipments(models.Model):
    equipment_name = models.CharField(max_length=50, null=False)
    equipment_category = models.ManyToManyField(EquipmentsCategories)
    weight_of_equipment_kg = models.FloatField(null=False)
    photo_of_equipment = models.CharField(max_length=255)
    now_booked = models.BooleanField(default=False)

    def __str__(self):
        return self.equipment_name

    # class Meta:
    #     ordering = ['equipment_name']








