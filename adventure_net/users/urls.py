from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("", views.checker, name="checker"),
    path("", views.get_equipments, name="get_equipments"), # table of equipment
    path("detail/<int:equipment_id>", views.detail_equipment, name="detail_equipment"), 
]
