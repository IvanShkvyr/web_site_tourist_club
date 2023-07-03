"""
Forms module for equipment-related forms.

This module defines various forms used in the equipment management system. These forms are
used for validating and processing user input related to equipment and bookings.

Classes:
    EquipmentsCategoriesForm: Form for creating or updating equipment categories.
    EquipmentsForm: Form for creating or updating equipment.
    BookingEquipmentsForm: Form for booking equipment.

"""

from datetime import datetime, timedelta

from django.forms import ModelForm, CharField, FloatField, NumberInput,\
    TextInput, ImageField, SelectDateWidget, DateField

from . import models


class EquipmentsCategoriesForm(ModelForm):
    """
    Form for creating or updating equipment categories.

    This form provides fields and validation for creating or updating equipment categories.

    Attributes:
        equipment_category_name (CharField): The name of the equipment category. It ensures
            that the category name is between 3 and 20 characters long.

    Methods:
        clean_equipment_category_name: Cleans and validates the equipment category name.

    """
    equipment_category_name = CharField(
                                        min_length=3,
                                        max_length=20,
                                        required=True,
                                        widget=TextInput()
                                        )

    def clean_equipment_category_name(self):
        """
        Clean and validate the equipment category name.

        Returns:
            str: The cleaned and validated equipment category name.

        """

        equipment_category_name = self.cleaned_data['equipment_category_name']
        return equipment_category_name.title()

    class Meta:
        model = models.EquipmentsCategories
        fields = ['equipment_category_name']


class EquipmentsForm(ModelForm):
    """
    Form for creating or updating equipment.

    This form provides fields and validation for creating or updating equipment.
    It ensures that the equipment name is between 3 and 50 characters long, and
    the weight is a positive float value.

    Attributes:
        equipment_name (CharField): The name of the equipment.
        weight_of_equipment_kg (FloatField): The weight of the equipment in kilograms.
        photo_of_equipment (ImageField): The photo of the equipment.
        equipment_description (CharField): The description of the equipment.

    Methods:
        clean_equipment_name: Cleans and validates the equipment name.

    """

    equipment_name = CharField(min_length=3, max_length=50, required=True, widget=TextInput())
    weight_of_equipment_kg = FloatField(min_value=0, required=True, widget=NumberInput())
    photo_of_equipment = ImageField(required=False)
    equipment_description = CharField(min_length=3, max_length=150, widget=TextInput())

    def clean_equipment_name(self):
        """
        Clean and validate the equipment name.

        Returns:
            str: The cleaned and validated equipment name.

        """

        equipment_name = self.cleaned_data['equipment_name']
        return equipment_name.capitalize()

    class Meta:
        model = models.Equipments
        fields = [
            'equipment_name',
            'equipment_category',
            'weight_of_equipment_kg',
            'photo_of_equipment',
            'equipment_description']
        exclude = ["equipment_category"]


class BookingEquipmentsForm(ModelForm):
    """
    Form for booking equipment.

    This form provides fields for booking equipment, including the booking date range.
    It sets the initial values for the booking date fields to today and tomorrow.

    Attributes:
        today (datetime.date): The current date.
        tomorrow (datetime.date): The date for tomorrow.
        booking_date_from (DateField): The booking start date.
        booking_date_to (DateField): The booking end date.

    """

    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)
    booking_date_from = DateField(required=True, widget=SelectDateWidget(), initial=today)
    booking_date_to = DateField(required=True, widget=SelectDateWidget(), initial=tomorrow)

    class Meta:
        model = models.EquipmentBooking
        fields = ['booking_date_from', 'booking_date_to']
