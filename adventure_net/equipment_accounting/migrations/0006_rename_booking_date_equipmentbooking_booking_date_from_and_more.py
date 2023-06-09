# Generated by Django 4.1.7 on 2023-06-13 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("equipment_accounting", "0005_remove_equipments_equipment_category_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="equipmentbooking",
            old_name="booking_date",
            new_name="booking_date_from",
        ),
        migrations.AddField(
            model_name="equipmentbooking",
            name="booking_date_to",
            field=models.DateField(blank=True, null=True),
        ),
    ]
