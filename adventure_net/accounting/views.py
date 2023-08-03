# pylint: disable=E1101
"""
Module: views.py

This module contains Django views for handling funds accounting record-related
functionality.
"""

from django.contrib import messages
from django.contrib.auth import decorators
from django.shortcuts import render, redirect, get_object_or_404

from adventure_net.messages import MSG_AMOUNT_ADDED, MSG_INVALID_DATA, \
    MSG_CAT_OPERATION_ADDED, MSG_TYPE_OPERATION_ADDED, MSG_ACCESS_DENIED, \
    MSG_TYPE_OPERATION_DELETE, MSG_CAT_OPERATION_DELETE, MSG_TYPE_OPERATION_UPDATED, \
    MSG_CAT_OPERATION_UPDATED, MSG_AMOUNT_UPDATED, MSG_CAT_OPERATION_DELETE_ERR, \
    MSG_TYPE_OPERATION_DELETE_ERR
from adventure_net.permissions import PER_CHANGE_AMOUNT
from users.models import Profile
from .models import OperationType, OperationCategory, ClubTreasury
from .forms import CategoryOperationForm, TypeOperationForm, ClubTreasuryForm


@decorators.login_required(login_url='/login/')
def add_club_treasury(request):
    """
    Add data of a funds accounting record

    This function adds data of a funds accounting record to the database.
    It also checks whether the user is logged in and has the permissions
    to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        add_club_treasury(request)
    """

    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")

    if request.method == "POST":
        form = ClubTreasuryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, MSG_AMOUNT_ADDED)
            return redirect(to="accounting:get_club_treasury")
        messages.error(request, MSG_INVALID_DATA)
        return render(
                        request,
                        "accounting/add_club_treasury.html",
                        context={"form": form}
                     )
    return render(
                request,
                "accounting/add_club_treasury.html",
                context={"form": ClubTreasuryForm()}
                )


@decorators.login_required(login_url='/login/')
def get_club_treasury(request):
    """
    Render the page with a list of a funds accounting record

    This function renders a page with a list of a funds accounting record. It also checks whether
    the user is logged in.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        get_club_treasury(request)
    """

    permission = permissions_checker(request)

    treasuries = ClubTreasury.objects.all()

    return render(
        request,
        "accounting/get_club_treasury.html",
        context={"treasuries": treasuries, "permission":permission}
    )


@decorators.login_required(login_url='/login/')
def change_club_treasury(request, treasury_id):
    """
    Change data of the funds accounting record

    This function changes the data of a funds accounting record in the database. It also checks
    whether the user is logged in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.
        treasury_id (int): The ID of the funds accounting record to be changed.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        chenge_club_treasury(request, treasury_id)
    """

    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")

    current_record = get_object_or_404(ClubTreasury, pk=treasury_id)
    if request.method == "POST":
        form = ClubTreasuryForm(request.POST, instance=current_record)

        if form.is_valid():
            form.save()
            messages.success(request, MSG_AMOUNT_UPDATED)
            return redirect(to="accounting:get_club_treasury")

        messages.error(request, MSG_INVALID_DATA)
        context = {"form": form, "current_record": current_record}
        return render(request, "accounting/chenge_club_treasury.html", context)
    form = ClubTreasuryForm(instance=current_record)
    contex = {"form": form, "current_record": current_record}
    return render(request, "accounting/chenge_club_treasury.html", contex)


@decorators.login_required(login_url='/login/')
def add_operation_category(request):
    """
    Add data of a category of operation

    This function adds data of a category of operation to the database. It also checks whether
    the user is logged in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        add_operation_category(request)
    """

    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")

    if request.method == "POST":
        form = CategoryOperationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, MSG_CAT_OPERATION_ADDED)
            return redirect(to="accounting:get_club_treasury")
        messages.error(request, MSG_INVALID_DATA)
        return render(
                        request,
                        "accounting/add_operation_category.html",
                        context={"form": form}
                     )
    return render(
                request,
                "accounting/add_operation_category.html",
                context={"form": CategoryOperationForm()}
                )


@decorators.login_required(login_url='/login/')
def get_operation_category(request):
    """
    Render the page with a list of a operation category

    This function renders a page with a list of a operation category. It also checks whether
    the user is logged in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        get_operation_category(request)
    """

    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")

    operation_categories = OperationCategory.objects.all()

    return render(
        request,
        "accounting/get_operation_category.html",
        context={"operation_categories": operation_categories}
    )


@decorators.login_required(login_url='/login/')
def change_operation_category(request, operation_category_id):
    """
    Change data of the operation category

    This function changes the data of a operation category in the database. It also checks
    whether the user is logged in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.
        operation_category_id (int): The ID of the operation category to be changed.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        chenge_operation_category(request, operation_category_id)
    """

    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")

    current_operation_category = get_object_or_404(OperationCategory, pk=operation_category_id)
    if request.method == "POST":
        form = CategoryOperationForm(request.POST, instance=current_operation_category)

        if form.is_valid():
            new_cat_name = form.cleaned_data["category_name"]

            object_new_category_name = OperationCategory.objects.filter(category_name=new_cat_name)
            if object_new_category_name.exclude(pk=operation_category_id).exists():
                context = {"form": form, "current_operation_category": current_operation_category}
                return render(request, "accounting/change_operation_category.html", context)

            form.save()
            messages.success(request, MSG_CAT_OPERATION_UPDATED)
            return redirect(to="accounting:get_operation_category")

        messages.error(request, MSG_INVALID_DATA)
        context = {"form": form, "current_operation_category": current_operation_category}
        return render(request, "accounting/change_operation_category.html", context)

    form = CategoryOperationForm(instance=current_operation_category)
    context = {"form": form, "current_operation_category": current_operation_category}
    return render(request, "accounting/change_operation_category.html", context)


@decorators.login_required(login_url='/login/')
def delete_operation_category(request, operation_category_id):
    """
    Delete operation category

    This function checks the permissions of the user associated with the given request
    to determine if they have the necessary rights for accounting funds management.
    This function deletes data for operation category based on the provided
    operation_category_id. It requires the user to be logged in. 

    Parameters:
        request (HttpRequest): The HTTP request object.
        operation_category_id (int): The ID of the operation category to be delete.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        delete_operation_category(request, operation_category_id)
    """

    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")

    operation_category = get_object_or_404(OperationCategory, pk=operation_category_id)
    if request.method == "POST":
        if ClubTreasury.objects.filter(operation_category=operation_category).exists():
            messages.error(request, MSG_CAT_OPERATION_DELETE_ERR)
            return redirect(to="accounting:get_operation_category")
        operation_category.delete()
        messages.success(request, MSG_CAT_OPERATION_DELETE)
        return redirect(to="accounting:get_operation_category")
    return render(request, "accounting/delete_operation_category.html")


@decorators.login_required(login_url='/login/')
def add_operation_type(request):
    """
    Add data of a type of operation

    This function adds data of a type of operation to the database. It also checks whether
    the user is logged in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        add_operation_type(request)
    """

    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")

    if request.method == "POST":
        form = TypeOperationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, MSG_TYPE_OPERATION_ADDED)
            return redirect(to="accounting:get_club_treasury")
        messages.error(request, MSG_INVALID_DATA)
        return render(
                        request,
                        "accounting/add_operation_type.html",
                        context={"form": form}
                     )
    return render(
                    request,
                    "accounting/add_operation_type.html",
                    context={"form": TypeOperationForm()}
                )


@decorators.login_required(login_url='/login/')
def get_operation_type(request):
    """
    Render the page with a list of a operation type

    This function renders a page with a list of a operation type. It also checks whether
    the user is logged in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        get_operation_type(request)
    """

    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")

    operation_types = OperationType.objects.all()

    return render(
        request,
        "accounting/get_operation_types.html",
        context={"operation_types": operation_types}
    )


@decorators.login_required(login_url='/login/')
def change_operation_type(request, operation_type_id):
    """
    Change data of the operation type.

    This function changes the data of a operation type in the database. It also checks
    whether the user is logged in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.
        operation_type_id (int): The ID of the operation type to be changed.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        chenge_operation_type(request, operation_type_id)
    """

    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")

    operation_type = get_object_or_404(OperationType, pk=operation_type_id)

    if request.method == "POST":
        form = TypeOperationForm(request.POST, instance=operation_type)

        if form.is_valid():
            new_type_name = form.cleaned_data["type_name"]
            object_new_type_name =  OperationType.objects.filter(type_name=new_type_name)
            if object_new_type_name.exclude(pk=operation_type_id).exists():
                context = {"form": form, "operation_type": operation_type}
                return render(request, "accounting/change_operation_type.html", context)

            form.save()
            messages.success(request, MSG_TYPE_OPERATION_UPDATED)
            return redirect(to="accounting:get_operation_type")

        messages.error(request, MSG_INVALID_DATA)
        context = {"form": form, "operation_type": operation_type}
        return render(request, "accounting/change_operation_type.html", context)

    form = TypeOperationForm(instance=operation_type)
    context = {"form": form, "operation_type": operation_type}
    return render(request, "accounting/change_operation_type.html",context)


@decorators.login_required(login_url='/login/')
def delete_operation_type(request, operation_type_id):
    """
    Delete operation type

    This function checks the permissions of the user associated with the given request
    to determine if they have the necessary rights for accounting funds management.
    This function deletes data for operation type based on the provided operation_type_id.
    It requires the user to be logged in. 

    Parameters:
        request (HttpRequest): The HTTP request object.
        operation_type_id (int): The ID of the operation type to be delete.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        delete_operation_type(request, operation_type_id)
    """

    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")

    operation_type = get_object_or_404(OperationType, pk=operation_type_id)
    if request.method == "POST":
        if ClubTreasury.objects.filter(operation_type=operation_type).exists():
            messages.error(request, MSG_TYPE_OPERATION_DELETE_ERR)
            return redirect(to="accounting:get_operation_type")
        operation_type.delete()
        messages.success(request, MSG_TYPE_OPERATION_DELETE)
        return redirect(to="accounting:get_operation_type")
    return render(request, "accounting/delete_operation_type.html")


def permissions_checker(request):
    """
    Check user permissions for accounting.

    This function checks the permissions of the user associated with the given request
    to determine if they have the necessary rights for accounting funds management. It
    verifies if the user's profile exists and if any of their positions have the required 
    category for changing data.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        bool: True - if the user has the necessary permissions, False - otherwise.

    Example:
        has_permissions = permissions_checker(request)
    """

    permission = True
    try:
        profile = request.user.profile
        user_positions = profile.user_position.all()
    except Profile.DoesNotExist:
        permission = False
        return permission

    allowed_positions = PER_CHANGE_AMOUNT

    if not any(position.positions_category in allowed_positions for position in user_positions):
        messages.error(request, MSG_ACCESS_DENIED)
        permission = False
        return permission
    return permission
