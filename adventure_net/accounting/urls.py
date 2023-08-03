from django.urls import path
from . import views

app_name = "accounting"

urlpatterns = [
    path("", views.get_club_treasury, name="get_club_treasury"),
    path("add_club_treasury/", views.add_club_treasury, name="add_club_treasury"),
    path("change_club_treasury/<int:treasury_id>/", views.change_club_treasury, name="change_club_treasury"),
    path("operation_category/", views.get_operation_category, name="get_operation_category"),
    path("operation_category/add_opr_category/", views.add_operation_category, name="add_operation_category"),
    path("operation_category/change_opr_category/<int:operation_category_id>/", views.change_operation_category, name="change_operation_category"),
    path("operation_category/delete_opr_category/<int:operation_category_id>/", views.delete_operation_category, name="delete_operation_category"),
    path("operation_type/", views.get_operation_type, name="get_operation_type"),
    path("operation_type/add_operation_type/", views.add_operation_type, name="add_operation_type"),
    path("operation_type/change_operation_type/<int:operation_type_id>/", views.change_operation_type, name="change_operation_type"),
    path("operation_type/delete_operation_type/<int:operation_type_id>/", views.delete_operation_type, name="delete_operation_type"),
]
