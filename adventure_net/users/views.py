"""
Module: views.py
 
This module contains Django views for handling user-related functionality.
"""
# pylint: disable=E1101

import secrets
import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, decorators
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from dotenv import load_dotenv

from adventure_net.messages import MSG_WELCOME, MSG_PLACEHOLDERS, MSG_USER_DATA_ADDED,\
    MSG_INVALID_DATA, MSG_ACCESS_DENIED, MSG_INVALID_USERNAME_OR_PASSWORD,\
    MSG_WELCOME_TOUR_CLUB, MSG_LOGIN_PASSWORD_RECOVERY, MSG_PASSWORD_RESET_INSTRUCTIONS, \
    MSG_EMAIL_NOT_FOUND, MSG_PASSWORD_RESET_LINK, MSG_USER_DATA_UPDATED, MSG_USER_DATA_DELETE, \
    MSG_MEMBERSHIP_ADDED, MSG_MEMBERSHIP_DATA_UPDATED, MSG_MEMBERSHIP_DATA_DELETE, \
    MSG_LOGIN_PASSWORD_UPDATED, MSG_UNTRUSTED_TOKEN
from adventure_net.permissions import PER_CHANGE_PROFILE
from .forms import RegisterForm, LoginForm, CategoryForm, MembersForm,\
    UpdateAccountInformationForm, RecoverLoginForm, ResetPasswordForm
from .models import Profile, RecoveryToken, UserPositions

load_dotenv()

def main(request):
    """
    Renders the main page.

    This function renders the main page. All users, including unregistered users, have access to
    this page.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        main(request)
    """

    return render(request, 'users/main.html', context={"msg": MSG_WELCOME})


def placeholders(request):
    """
    Renders a page with a message indicating that the page is under development.

    This function renders a page with a message indicating that the page is under development.
    All users, including unregistered users, have access to this page.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        placeholders(request)
    """

    return render(request, 'users/placeholders.html', context={"msg": MSG_PLACEHOLDERS})


def signup_user(request):
    """
    Registers a new user.

    This function creates a new user after validating the filled form. It allows user creation
    only for users who have the necessary permissions. Upon successful data entry, the function
    redirects to the main page and displays a success message. If the action is unsuccessful,
    an appropriate message is displayed and the user is prompted to enter the data again.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        signup_user(request)
    """

    permission = permissions_signup_checker(request)
    if not permission:
        return redirect(to="users:club_members")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, MSG_USER_DATA_ADDED)
            return redirect(to="users:main")
        messages.error(request, MSG_INVALID_DATA)
        return render(request, 'users/singup.html', context={'form': form})
    return render(request, 'users/singup.html', context={'form': RegisterForm()})


def login_user(request):
    """
    Authenticates a user.

    This function authenticates a user. At the beginning of the function, it checks if the
    user is already authenticated. If so, it redirects the user to the main page. If the
    user is not found, an error message for invalid login or password is displayed.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        login_user(request)
    """

    if request.user.is_authenticated:
        return redirect(to="users:main")

    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is None:
            messages.error(request, MSG_INVALID_USERNAME_OR_PASSWORD)
            return redirect(to='users:login')
        login(request, user)
        messages.success(request, MSG_WELCOME_TOUR_CLUB)
        return redirect(to="users:main")
    return render(request, 'users/login.html', context={'form': LoginForm()})


@decorators.login_required
def logout_user(request):
    """
    Logs out a user.

    This function logs out a user by removing them from the session and redirecting them
    to the main page.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        logout_user(request)
    """

    logout(request)
    return redirect(to="users:main")


def recover_login_password(request):
    """ 
    Recovers the login password.

    This function is designed to send a password recovery link to the user. At the beginning
    of the function, it checks if the user is already authenticated. If the user is
    authenticated, they are redirected to the main page. After that, the function checks if
    the entered email address is present in the database. If the email address is found, a
    token is generated and stored in the database. The token is then sent to the user's email
    address as a link. If the email address is not found, an error message is displayed.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        recover_login_password(request)
    """

    if request.user.is_authenticated:
        return redirect(to="users:main")

    if request.method == 'POST':
        form = RecoverLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                profile = Profile.objects.get(email=email)
                user = profile.user

            except User.DoesNotExist:
                user = None
            if user:
                token = secrets.token_urlsafe(32)
                RecoveryToken.objects.create(token=token, user=user)
                reset_url = request.build_absolute_uri(
                                                reverse('users:reset_password', args=[token])
                                                      )

                send_mail(
                    MSG_LOGIN_PASSWORD_RECOVERY,
                    f'{MSG_PASSWORD_RESET_LINK} {reset_url}',
                    os.getenv('EMAIL_HOST_USER'),
                    [email],
                    fail_silently=False,
                )
                messages.success(
                                request,
                                MSG_PASSWORD_RESET_INSTRUCTIONS
                                )
                return render(request, "users/main.html")
            messages.error(
                            request,
                            MSG_EMAIL_NOT_FOUND
                            )
            return render(request, "users/main.html")
    else:
        form = RecoverLoginForm()

    return render(request, 'users/recover.html', {'form': form})


def reset_password(request, token):
    """ 
    Resets the user's password.

    This function is responsible for resetting the user's password. If the user is already
    authenticated, they are redirected to the main page. If the request method is GET, the
    function verifies the validity of the token received. If the token is invalid or does not
    exist in the database, an appropriate error response is returned. If the token is valid,
    the corresponding user's information is retrieved, including the username, and rendered
    on the reset password page along with the token. If the request method is POST, the function
    validates the submitted password form. If the form is valid, the user's password is updated
    with the new password, and the recovery token is deleted from the database. The user is then
    redirected to the password_reset_success page.


    Parameters:
        request (HttpRequest): The HTTP request object.
        token (str): The reset token received by the user.

    Returns:
        HttpResponse or None: The HTTP response object or None.

    Example:
        reset_password(request, token)
    """

    if request.user.is_authenticated:
        return redirect(to="users:main")

    if request.method =="GET":
        try:
            recovery_token = RecoveryToken.objects.get(token=token)
        except RecoveryToken.DoesNotExist:
            return HttpResponse(MSG_UNTRUSTED_TOKEN)

        user = recovery_token.user
        user_login = user.username

        return render(request, "users/reset_password.html", {"token":token, "login":user_login})

    elif request.method == "POST":
        form = ResetPasswordForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data["password"]

            try:
                recovery_token = RecoveryToken.objects.get(token=token)
            except RecoveryToken.DoesNotExist:
                return HttpResponse(MSG_UNTRUSTED_TOKEN)

            user = recovery_token.user
            user.set_password(password)
            user.save()

            recovery_token.delete()

            return redirect('users:password_reset_success')

        return render(request, 'users/reset_password.html', {'form': form, 'token': token})


def password_reset_success(request):
    """ 
    Renders the password reset success page.

    This function is responsible for rendering the password reset success page. If the user
    is already authenticated, they are redirected to the main page.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        password_reset_success(request)
    """

    if request.user.is_authenticated:
        return redirect(to="users:main")
    return render(request, 'users/password_reset_success.html')


@decorators.login_required(login_url='/login/')
def profile_user(request, user_id):
    """ 
    Displays user profile information.

    This function is responsible for rendering the page displaying the full user profile
    information. It first checks if the user is authenticated. It also provides information
    about permission to edit the profile.

    
    Parameters:
        request (HttpRequest): The HTTP request object.
        user_id (int): The ID of the user.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        profile_user(request, user_id)
    """

    allowed_positions = PER_CHANGE_PROFILE
    profile = request.user.profile
    has_permission = profile.user_position.filter(positions_category__in=allowed_positions).exists()

    user_profile = get_object_or_404(Profile, user_id=user_id)
    user_login = user_profile.user.username
    return render(request, 'users/profile.html', context={
                                                            'users': user_profile,
                                                            'login': user_login,
                                                            'has_permission':has_permission
                                                            })


@decorators.login_required(login_url='/login/')
def get_users(request):
    """ 
    Displays a list of users.

    This function is responsible for rendering the page displaying a list of users. 
    It first checks if the user is authenticated and has permission to view the users.
    It retrieves all the user profiles and passes them to the template for rendering.
    
    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        get_users(request)
    """

    allowed_positions = PER_CHANGE_PROFILE
    profile = request.user.profile
    has_permission = profile.user_position.filter(positions_category__in=allowed_positions).exists()

    members = Profile.objects.all()
    return render(
                    request,
                    "users/club_members.html",
                    context={"members": members, "has_permission":has_permission}
                )


@decorators.login_required(login_url='/login/')
def change_profile(request, user_id):
    """ 
    Function for changing user profile data.

    This function is responsible for changing user profile data. It first checks if the user is
    authenticated and has permission to edit the profile. If the submitted form is valid, the
    modified data is saved to the database and a corresponding success message is displayed.
    If the form is not valid, an error message is displayed and the user is prompted to fill out
    the form again.
    
    Parameters:
        request (HttpRequest): The HTTP request object.
        user_id (int): The ID of the user.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        change_profile(request, user_id)
    """

    member = get_object_or_404(Profile, pk=user_id)

    allowed_positions = PER_CHANGE_PROFILE
    profile = request.user.profile
    has_permission = profile.user_position.filter(positions_category__in=allowed_positions).exists()

    if member.user != request.user and not has_permission:
        messages.error(request, MSG_ACCESS_DENIED)
        return redirect(to='users:club_members')

    if request.method == "POST":
        form = MembersForm(request.POST or None, request.FILES or None, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, MSG_USER_DATA_UPDATED)
            return redirect('users:club_members')
    else:
        messages.error(request, MSG_INVALID_DATA)
        form = MembersForm(instance=member)
    return render(
                request,
                'users/change_profile.html',
                context={'form': form, 'member': member, "has_permission":has_permission}
                )


@decorators.login_required(login_url='/login/')
def delete_profile(request, user_id):
    """ 
    Function for deleting user profile data.

    This function is responsible for deleting user profile data.
    It first checks if the user is authenticated and has permission to edit the profile.
    If the user has permission to delete the profile, the corresponding record is deleted.
    
    Parameters:
        request (HttpRequest): The HTTP request object.
        user_id (int): The ID of the user.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        delete_profile(request, user_id)
    """
    
    permission = permissions_signup_checker(request)
    if not permission:
        return redirect(to="users:club_members")

    if request.method == "POST":
        member = get_object_or_404(Profile, pk=user_id)
        user = member.user

        User.objects.filter(pk = user.id).delete()
        messages.success(request, MSG_USER_DATA_DELETE)
        return redirect(to="users:club_members")
    return render(request, "users/delete_user.html")



@decorators.login_required(login_url='/login/')
def get_user_position(request):
    """ 
    Function for displaying a list of user positions.

    This function is responsible for displaying a list of user positions.
    It first checks if the user is authenticated and has permission to view the user position list.
    
    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        get_user_position(request)
    """

    permission = permissions_signup_checker(request)
    if not permission:
        return redirect(to="users:club_members")

    user_positions = UserPositions.objects.all()
    return render(
                    request,
                    "users/user_positions.html",
                    context={"user_positions": user_positions}
                )


@decorators.login_required(login_url='/login/')
def add_user_position(request):
    """ 
    Function for adding user positions.

    This function is responsible for adding user positions.
    It first checks if the user is authenticated and has permission to view the user position list.
    
    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        add_user_position(request)
    """

    permission = permissions_signup_checker(request)
    if not permission:
        return redirect(to="users:club_members")

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, MSG_MEMBERSHIP_ADDED)
            return redirect(to='users:get_user_position')
        messages.error(request, MSG_INVALID_DATA)
        return render(
                        request,
                        "users/add_user_position.html",
                        context={"form": form}
                    )
    return render(
                    request,
                    "users/add_user_position.html",
                    context={"form": CategoryForm()}
                 )


@decorators.login_required(login_url='/login/')
def change_user_position(request, position_id):
    """ 
    Function for changing user positions.

    This function is responsible for changing user positions.
    It first checks if the user is authenticated and has permission to view the user position list.
    
    Parameters:
        request (HttpRequest): The HTTP request object.
        position_id (int): The ID of the position.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        change_user_position(request, position_id)
    """

    permission = permissions_signup_checker(request)
    if not permission:
        return redirect(to="users:club_members")

    user_position = get_object_or_404(UserPositions, pk=position_id)
    if request.method == "POST":
        form = CategoryForm(request.POST)
        user_positions_category = request.POST["positions_category"]
        if form.is_valid() and user_position.positions_category != user_positions_category:
            UserPositions.objects.filter(pk=position_id).update(
                positions_category=request.POST["positions_category"],
                positions_category_info=request.POST["positions_category_info"]
            )
            return redirect(to="users:get_user_position")
        if user_position.positions_category == request.POST["positions_category"]:
            UserPositions.objects.filter(pk=position_id).update(
                positions_category_info=request.POST["positions_category_info"]
            )
            messages.success(request, MSG_MEMBERSHIP_DATA_UPDATED)
            return redirect(to="users:get_user_position")
        messages.error(request, MSG_INVALID_DATA)
        return render(
            request,
            "users/change_user_position.html",
            context={"form": form, "user_position": user_position, "position_id": position_id},
        )
    form = CategoryForm(instance=user_position)
    return render(
                    request,
                    "users/change_user_position.html",
                    context={"form": form, "user_position": user_position}
                 )


@decorators.login_required(login_url='/login/')
def delete_user_position(request, position_id):
    """ 
    Function for deleting user positions.

    This function is responsible for deleting user positions.
    It first checks if the user is authenticated and has permission to view the user position list.
    
    Parameters:
        request (HttpRequest): The HTTP request object.
        position_id (int): The ID of the position.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        change_user_position(request, position_id)
    """

    permission = permissions_signup_checker(request)
    if not permission:
        return redirect(to="users:club_members")

    if request.method == "POST":
        UserPositions.objects.filter(pk = position_id).delete()
        messages.success(request, MSG_MEMBERSHIP_DATA_DELETE)
        return redirect(to="users:get_user_position")
    return render(request, "users/delete_user_position.html")


@decorators.login_required(login_url='/login/')
def update_account_information(request, user_id):
    """ 
    Function for updating user login and password information.

    This function is responsible for updating the login and password information of a user.
    It first checks if the user is authenticated and has permission to view the user position list.
    
    Parameters:
        request (HttpRequest): The HTTP request object.
        user_id (int): The ID of the user.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        change_user_position(request, user_id)
    """

    member = get_object_or_404(Profile, pk=user_id)

    if member.user != request.user:
        messages.error(request, MSG_ACCESS_DENIED)
        return redirect(to='users:club_members')

    user = member.user

    if request.method == "POST":
        form = UpdateAccountInformationForm(request.POST, instance=user)
        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, MSG_LOGIN_PASSWORD_UPDATED)
            return redirect('users:club_members')
        messages.error(request, MSG_INVALID_DATA)
    else:
        form = UpdateAccountInformationForm(instance=user)

    return render(
        request,
        'users/update_account_information.html',
        context={'form': form, 'member': member}
    )


def permissions_signup_checker(request):
    """ 
    Function that provides permissions to the user.

    This function checks the user's position and returns the permission variable accordingly.
    It first checks if the user is authenticated and has permission to view the user position list.
    
    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        permission (bool): A boolean indicating whether the user has permission.

    Example:
        permissions_signup_checker(request)
    """

    permission = True
    try:
        profile = request.user.profile
        user_positions = profile.user_position.all()
    except Profile.DoesNotExist:
        permission = False
        return permission

    allowed_positions = PER_CHANGE_PROFILE

    if not any(position.positions_category in allowed_positions for position in user_positions):
        messages.error(request, MSG_ACCESS_DENIED)
        permission = False
        return permission
    return permission
