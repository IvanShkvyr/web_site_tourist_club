from django.urls import path
from . import views

app_name = "accounting"

urlpatterns = [
    path("", views.get_club_treasury, name="get_club_treasury"),
    path("add_club_treasury/", views.add_club_treasury, name="add_club_treasury"),
    path("chenge_club_treasury/<int:treasury>/", views.chenge_club_treasury, name="chenge_club_treasury"),
    path("operation_category/", views.get_operation_category, name="get_operation_category"),
    path("operation_category/add_opr_category/", views.add_operation_category, name="add_operation_category"),
    path("operation_category/chenge_opr_category/<int:operation_category>/", views.chenge_operation_category, name="chenge_operation_category"),
    path("operation_category/delete_opr_category/<int:operation_category>/", views.delete_operation_category, name="delete_operation_category"),
    path("operation_type/", views.get_operation_type, name="get_operation_type"),
    path("operation_type/add_operation_type/", views.add_operation_type, name="add_operation_type"),
    path("operation_type/chenge_operation_type/<int:operation_type>/", views.chenge_operation_type, name="chenge_operation_type"),
    path("operation_type/delete_operation_type/<int:operation_type>/", views.delete_operation_type, name="delete_operation_type"),
]

