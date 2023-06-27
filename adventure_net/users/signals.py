from django.db.models.signals import post_save, post_migrate
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Profile, UserPositions

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_migrate)
def create_user_positions(sender, **kwargs):
    if sender.name == 'users':
        positions = [
            {'positions_category': 'Head', 'positions_category_info': 'Club leader overseeing operations and decision-making.'},
            {'positions_category': 'Member', 'positions_category_info': 'Club member participating in club activities and events.'},
            {'positions_category': 'Equipment manager', 'positions_category_info': 'Steward managing and organizing club equipment and supplies.'},
            {'positions_category': 'Accountant', 'positions_category_info': 'Accountant responsible for financial management and bookkeeping.'},
            {'positions_category': 'Sports events organizer', 'positions_category_info': 'Sports events organizer coordinating athletic activities and competitions.'},
            {'positions_category': 'Events organizer', 'positions_category_info': 'Events organizer planning and executing various club events.'},
        ]
        for position in positions:
            category = position['positions_category']
            category_info = position['positions_category_info']
            UserPositions.objects.get_or_create(positions_category=category, defaults={'positions_category_info': category_info})