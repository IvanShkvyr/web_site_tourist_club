"""
Module for handling signals and receivers related to user profiles and positions.

This module contains signal receiver functions that are triggered by specific events
in the Django framework. The receivers in this module handle the creation and saving of
user profiles, as well as the creation of predefined user positions.

Signals and Receivers:
- create_profile: Creates a profile for a user after a User object is saved.
- save_profile: Saves the profile associated with a User object after it is saved.
- create_user_positions: Creates predefined UserPositions objects after migrations are run.
"""

from django.db.models.signals import post_save, post_migrate
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Profile, UserPositions

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Signal receiver function to create a profile for a user.

    This function is triggered after a User object is saved. If a new user is created,
    it creates a corresponding Profile object for that user.

    Parameters:
        sender (Model): The sender model class.
        instance (User): The User instance that was saved.
        created (bool): A boolean flag indicating whether the user was created.

    Returns:
        None

    Example:
        create_profile(sender, instance, created)
    """

    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Signal receiver function to save a user's profile.

    This function is triggered after a User object is saved. It saves the associated
    Profile object for that user.

    Parameters:
        sender (Model): The sender model class.
        instance (User): The User instance that was saved.

    Returns:
        None

    Example:
        save_profile(sender, instance)
    """

    instance.profile.save()


@receiver(post_migrate)
def create_user_positions(sender, **kwargs):
    """
    Signal receiver function to create user positions.

    This function is triggered after migrations are run. If the migrated app is the 'users' app,
    it creates predefined UserPositions objects representing different positions.

    Parameters:
        sender (Module): The sender module that triggered the signal.

    Returns:
        None

    Example:
        create_user_positions(sender)
    """

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
