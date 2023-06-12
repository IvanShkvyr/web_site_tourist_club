from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("", views.main, name="main"),
    path("singup/", views.signup_user, name="signup"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("profile/<int:user_id>/", views.profile_user, name="profile"),
    path("club_members/", views.get_users, name="club_members"),
    path("change_profile/<int:user_id>/", views.change_profile, name="change_profile"),
    path("get_user_position/", views.get_user_position, name="get_user_position"),
    path("add_user_position/", views.add_user_position, name="add_user_position"),
    path("change_user_position/<int:position_id>/", views.change_user_position, name="change_user_position"),
    path("delete_user_position/<int:position_id>/", views.delete_user_position, name="delete_user_position"),
    path("placeholders/", views.placeholders, name="placeholders"),
]

