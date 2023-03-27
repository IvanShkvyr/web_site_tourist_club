from django.urls import path
from . import views

app_name = "equipment"

urlpatterns = [
    path("checker/", views.checker, name="checker"),
]
