from django.urls import path
from . import views

app_name = "equipment"

urlpatterns = [
    path("", views.get_equipments, name="get_equipments"), # table of equipment
    path("detail/<int:equipment_id>", views.detail_equipment, name="detail_equipment"), # show detail about equipment
    path("add_equipment/", views.add_equipment, name="add_equipment"), # add equipment to table
    path("change_equipment/<int:equipment_id>", views.change_equipment, name="change_equipment"), # change equipment in table
    path("delete_equipment/<int:equipment_id>", views.delete_equipment, name="delete_equipment"), # delete equipment in table
    path("category/", views.get_category, name="get_category"), # table of equipment categories
    path("category/add_category", views.add_category, name="add_category"), # add equipment category
    path("category/change_category/<int:category_id>", views.change_category, name="change_category"), # change equipment category
    path("category/delete_category/<int:category_id>", views.delete_category, name="delete_category"), # delete equipment category
    path("book_equipment/<int:equipment_id>", views.book_equipment, name="book_equipment"),
    path("get_book_equipment/<int:equipment_id>", views.get_book_equipment, name="get_book_equipment"),
    path("cancel_equipment_reservation/<int:book_equipment_id>", views.cancel_equipment_reservation, name="cancel_equipment_reservation"),
]
