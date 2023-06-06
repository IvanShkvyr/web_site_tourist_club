from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("", views.main, name="main"),
    path("singup/", views.signup_user, name="signup"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("profile/<int:user_id>/", views.profile_user, name="profile"),
]