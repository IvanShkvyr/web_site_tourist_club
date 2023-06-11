# Generated by Django 4.1.7 on 2023-06-11 04:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("equipment_accounting", "0002_remove_equipments_equipment_category_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="equipments",
            name="now_booked",
        ),
        migrations.AddField(
            model_name="equipments",
            name="current_user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="equipments",
            name="equipment_description",
            field=models.CharField(default="-", max_length=150),
        ),
        migrations.AlterField(
            model_name="equipments",
            name="photo_of_equipment",
            field=models.ImageField(
                default="default_tool.png", upload_to="equipment_images"
            ),
        ),
        migrations.CreateModel(
            name="EquipmentBooking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("booking_date", models.DateField()),
                (
                    "club_member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reserved_equipment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="equipment_accounting.equipments",
                    ),
                ),
            ],
        ),
    ]
