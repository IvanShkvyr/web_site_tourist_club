# Generated by Django 4.1.7 on 2023-06-05 12:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserPositions",
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
                ("positions_category", models.CharField(max_length=20, unique=True)),
                ("positions_category_info", models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name="Profile",
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
                ("user_name", models.CharField(max_length=50)),
                ("user_lastname", models.CharField(max_length=50)),
                ("user_birthday", models.DateField()),
                (
                    "user_avatar",
                    models.ImageField(
                        default="avatar_default.png", upload_to="profile_images"
                    ),
                ),
                ("user_experience", models.CharField(max_length=250)),
                ("user_location", models.CharField(max_length=50)),
                ("user_info", models.CharField(max_length=250)),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None
                    ),
                ),
                ("email", models.EmailField(max_length=100)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("user_position", models.ManyToManyField(to="users.userpositions")),
            ],
        ),
    ]
