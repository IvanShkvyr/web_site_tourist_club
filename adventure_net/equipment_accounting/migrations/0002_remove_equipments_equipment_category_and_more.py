# Generated by Django 4.1.7 on 2023-04-26 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("equipment_accounting", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="equipments",
            name="equipment_category",
        ),
        migrations.AddField(
            model_name="equipments",
            name="equipment_category",
            field=models.ManyToManyField(
                to="equipment_accounting.equipmentscategories"
            ),
        ),
    ]