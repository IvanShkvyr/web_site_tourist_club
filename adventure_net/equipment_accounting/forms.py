from django.forms import ModelForm, CharField, FloatField, NumberInput, TextInput, ModelChoiceField
from . import models


class EquipmentsCategoriesForm(ModelForm):
    equipment_category_name = CharField(min_length=3, max_length=20, required=True, widget=TextInput())

    class Meta:
        model = models.EquipmentsCategories
        fields = ['equipment_category_name']


class EquipmentsForm(ModelForm):
    equipment_name = CharField(min_length=3, max_length=50, required=True, widget=TextInput())
    weight_of_equipment_kg = FloatField(min_value=0, required=True, widget=NumberInput())
    photo_of_equipment = CharField(max_length=255, required=True, widget=TextInput())

    class Meta:
        model = models.Equipments
        fields = ['equipment_name', 'weight_of_equipment_kg', 'photo_of_equipment']
        exclude = ["equipment_category"]


