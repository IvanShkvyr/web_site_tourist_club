from datetime import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from PIL import Image, ImageOps


class EquipmentsCategories(models.Model):
    equipment_category_name = models.CharField(max_length=20, unique=True, null=False)

    def __str__(self):
        return self.equipment_category_name


class Equipments(models.Model):
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
            # Змінюємо розміри зображення до 225x225 пікселів
            # зображення не обрізається . залишається його пропорція
            # pic.save(self.photo_of_equipment.path)


        # Змінюємо розміри зображення до 225x225 пікселів,зображення обрізається по центру
        # resized_image = ImageOps.fit(pic, (225, 225), Image.ANTIALIAS)

        # Створюємо нове зображення квадратної форми з білим фоном
        square_image = Image.new('RGB', (225, 225), (255, 255, 255))
        # square_image.paste(resized_image, ((225 - resized_image.size[0]) // 2, (225 - resized_image.size[1]) // 2))
        square_image.paste(pic, ((225 - pic.size[0]) // 2, (225 - pic.size[1]) // 2))

        # Зберігаємо зображення
        square_image.save(self.photo_of_equipment.path)




class EquipmentBooking(models.Model):
    club_member = models.ForeignKey(User, on_delete=models.CASCADE)
    reserved_equipment = models.ForeignKey(Equipments, on_delete=models.CASCADE)
    booking_date_from = models.DateField()
    booking_date_to = models.DateField(default=timezone.now)

    def __str__(self):
        return self.club_member








