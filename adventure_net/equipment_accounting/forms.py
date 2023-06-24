from datetime import datetime, timedelta

from django.forms import BooleanField, ModelForm, CharField,\
      FloatField, NumberInput, TextInput, ModelChoiceField,\
      ModelMultipleChoiceField, SelectMultiple, ImageField,\
      SelectDateWidget, DateField

from . import models


class EquipmentsCategoriesForm(ModelForm):
    equipment_category_name = CharField(min_length=3, max_length=20, required=True, widget=TextInput())

    def clean_equipment_category_name(self):
        equipment_category_name = self.cleaned_data['equipment_category_name']
        return equipment_category_name.title()

    class Meta:
        model = models.EquipmentsCategories
        fields = ['equipment_category_name']


class EquipmentsForm(ModelForm):
    equipment_name = CharField(min_length=3, max_length=50, required=True, widget=TextInput())
    weight_of_equipment_kg = FloatField(min_value=0, required=True, widget=NumberInput())
    photo_of_equipment = ImageField(required=False)
    equipment_description = CharField(min_length=3, max_length=150, widget=TextInput())

    def clean_equipment_name(self):
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
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)
    booking_date_from = DateField(required=True, widget=SelectDateWidget(), initial=today)
    booking_date_to = DateField(required=True, widget=SelectDateWidget(), initial=tomorrow)

    class Meta:
        model = models.EquipmentBooking
        fields = ['booking_date_from', 'booking_date_to']
