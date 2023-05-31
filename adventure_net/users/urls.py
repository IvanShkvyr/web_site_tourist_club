from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("singup/", views.signup_user, name="signup"),
    # path("login/", views.login_user, name="login"),
    # path("logout/", views.logout_user, name="logout"),
    # path("profile/", views.profile_user, name="profile"),
]
