from datetime import datetime
from django.forms import CharField, ModelForm, TextInput, NumberInput, FloatField,\
    ModelChoiceField

from django.contrib.auth.models import User

from . import models


class CategoryOperationForm(ModelForm):
    category_name = CharField(min_length=3,
                                   max_length=20,
                                   required=True,
                                   widget=TextInput()
                                   )
    category_info = CharField(
                                min_length=10,
                                max_length=100,
                                required=True,
                                widget=TextInput()
                                )

    class Meta:
        model = models.OperationCategory
        fields = ['category_name', 'category_info']

class TypeOperationForm(ModelForm):
    type_name = CharField(min_length=3,
                                   max_length=20,
                                   required=True,
                                   widget=TextInput()
                                   )
    type_info = CharField(
                                min_length=10,
                                max_length=100,
                                required=True,
                                widget=TextInput()
                                )

    class Meta:
        model = models.OperationCategory
        fields = ['type_name', 'type_info']


class ClubTreasuryForm(ModelForm):
    amount =  FloatField(min_value=0, required=True, widget=NumberInput())
    info = CharField(
                                min_length=10,
                                max_length=50,
                                required=True,
                                widget=TextInput()
                                )
    
    operation_category = ModelChoiceField(queryset=models.OperationCategory.objects.all(), required=True)
    operation_type = ModelChoiceField(queryset=models.OperationType.objects.all(), required=True)
    performed_by = ModelChoiceField(queryset=User.objects.all(), required=False)

    class Meta:
        model = models.ClubTreasury
        fields = ['amount', 'info', 'operation_category', 'operation_type', 'performed_by']



