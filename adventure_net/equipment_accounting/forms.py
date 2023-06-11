from django.forms import BooleanField, ModelForm, CharField,\
      FloatField, NumberInput, TextInput, ModelChoiceField,\
      ModelMultipleChoiceField, SelectMultiple, ImageField

from . import models


class EquipmentsCategoriesForm(ModelForm):
    equipment_category_name = CharField(min_length=3, max_length=20, required=True, widget=TextInput())

    class Meta:
        model = models.EquipmentsCategories
        fields = ['equipment_category_name']


class EquipmentsForm(ModelForm):
    equipment_name = CharField(min_length=3, max_length=50, required=True, widget=TextInput())
    # equipment_category = ModelMultipleChoiceField(
    #     queryset=models.EquipmentsCategories.objects.all(),
    #     widget=SelectMultiple,
    #     required=True
    # )
    weight_of_equipment_kg = FloatField(min_value=0, required=True, widget=NumberInput())
    photo_of_equipment = ImageField(required=False)
    equipment_description = CharField(min_length=3, max_length=150, widget=TextInput())

    class Meta:
        model = models.Equipments
        fields = [
            'equipment_name',
            'equipment_category',
            'weight_of_equipment_kg',
            'photo_of_equipment',
            'equipment_description']
        exclude = ["equipment_category"]
        # widgets = {
        #     'equipment_category': SelectMultiple(attrs={'class': 'form-control'}),
        # }
        


