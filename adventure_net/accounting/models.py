from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class OperationType(models.Model):
    type_name = models.CharField(max_length=20, null=False)
    type_info = models.CharField(max_length=100, null=False)


class OperationCategory(models.Model):
    category_name = models.CharField(max_length=20, null=False)
    category_info = models.CharField(max_length=100, null=False)


class ClubTreasury(models.Model):
    amount = models.FloatField(null=False)
    operation_date = models.DateField(default=timezone.now)
    purpose = models.CharField(max_length=50, null=False)
    operation_category = models.ForeignKey(OperationCategory, on_delete=models.CASCADE)
    operation_type = models.ForeignKey(OperationType, on_delete=models.CASCADE)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)

