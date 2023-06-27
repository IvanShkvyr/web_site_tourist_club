from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("", views.main, name="main"),
    path("singup/", views.signup_user, name="signup"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("recover/", views.recover_login_password, name="recover_login_password"),
    path("reset/<str:token>/", views.reset_password, name="reset_password"),
    path('password_reset_success/', views.password_reset_success, name='password_reset_success'),
    path("profile/<int:user_id>/", views.profile_user, name="profile"),
    path("club_members/", views.get_users, name="club_members"),
    path("change_profile/<int:user_id>/", views.change_profile, name="change_profile"),
    path("delete_profile/<int:user_id>/", views.delete_profile, name="delete_profile"),
    path("get_user_position/", views.get_user_position, name="get_user_position"),
    path("add_user_position/", views.add_user_position, name="add_user_position"),
    path("change_user_position/<int:position_id>/", views.change_user_position, name="change_user_position"),
    path("delete_user_position/<int:position_id>/", views.delete_user_position, name="delete_user_position"),
    path("placeholders/", views.placeholders, name="placeholders"),
    path("update_account_information/<int:user_id>/", views.update_account_information, name="update_account_information"),
]

