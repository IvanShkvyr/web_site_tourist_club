# pylint: disable=E1101
"""
Module: views.py

This module contains Django views for handling equipment-related functionality.
"""

from datetime import datetime, date

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from adventure_net.messages import MSG_INVALID_DATA, MSG_ACCESS_DENIED,\
    MSG_EQUIPMENT_CATEGORY_ADDED, MSG_EQUIPMENT_CATEGORY_UPDATED, MSG_EQUIPMENT_CATEGORY_DELETED,\
    MSG_EQUIPMENT_ADDED, MSG_EQUIPMENT_UPDATED, MSG_EQUIPMENT_DELETED, MSG_INVALID_START_DATE,\
    MSG_INVALID_END_DATE, MSG_INVALID_BOOKING_DURATION, MSG_INVALID_BOOKING_PERIOD_OVERLAP,\
    MSG_EQUIPMENT_RESERVED_SUCCESSFULLY, MSG_BOOKING_PERIOD_DELETED
from adventure_net.permissions import PER_CHANGE_EQUIPMENTS
from users.models import Profile
from .forms import EquipmentsForm, EquipmentsCategoriesForm, BookingEquipmentsForm
from .models import Equipments, EquipmentsCategories, EquipmentBooking


@login_required(login_url='/login/')
def get_category(request):
    """
    Render the page with a list of equipment categories

    This function renders a page with a list of equipment categories. It also checks whether
    the user is logged in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        get_category(request)
    """

    permission = permissions_equipment_checker(request)
    if not permission:
        return redirect(to="equipment:get_equipments")

    categories = EquipmentsCategories.objects.all()
    return render(
                    request,
                    "equipment_accounting/category.html",
                    context={"categories": categories}
                )


@login_required(login_url='/login/')
def add_category(request):
    """
    Add data of the category of equipment

    This function adds data of a category of equipment to the database. It also checks whether
    the user is logged in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        add_category(request)
    """

    permission = permissions_equipment_checker(request)
    if not permission:
        return redirect(to="equipment:get_equipments")

    if request.method == "POST":
        form = EquipmentsCategoriesForm(request.POST)
        if form.is_valid():
            data_equipment_categorie = form.save(commit=False)
            data_equipment_categorie.save()
            messages.success(request, MSG_EQUIPMENT_CATEGORY_ADDED)
            return redirect(to='equipment:get_category')

        messages.error(request, MSG_INVALID_DATA)
        return render(
                        request,
                        "equipment_accounting/add_category.html",
                        context={"form": form}
                    )
    return render(
                    request,
                    "equipment_accounting/add_category.html",
                    context={"form": EquipmentsCategoriesForm()}
                 )


@login_required(login_url='/login/')
def change_category(request, category_id):
    """
    Change data of the category of equipment.

    This function changes the data of a category of equipment in the database. It also checks
    whether the user is logged in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.
        category_id (int): The ID of the category to be changed.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        change_category(request)
    """

    permission = permissions_equipment_checker(request)
    if not permission:
        return redirect(to="equipment:get_equipments")

    category = get_object_or_404(EquipmentsCategories, pk=category_id)
    if request.method == "POST":
        form = EquipmentsCategoriesForm(request.POST)
        if form.is_valid():
            EquipmentsCategories.objects.filter(pk=category_id).update(
                equipment_category_name=request.POST["equipment_category_name"],
                )
            messages.success(request, MSG_EQUIPMENT_CATEGORY_UPDATED)
            return redirect(to="equipment:get_category")

        messages.error(request, MSG_INVALID_DATA)
        return render(
            request, "equipment_accounting/change_category.html", context={"form": form}
        )
    return render(
                  request,
                  "equipment_accounting/change_category.html",
                  context={"category": category}
                 )


@login_required(login_url='/login/')
def delete_category(request, category_id):
    """
    Delete data of the category of equipment

    This function deletes the data of a category of equipment from the database. It also
    checks whether the user is logged in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.
        category_id (int): The ID of the category to be changed.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        delete_category(request)
    """
    permission = permissions_equipment_checker(request)
    if not permission:
        return redirect(to="equipment:get_equipments")
    if request.method == "POST":
        EquipmentsCategories.objects.filter(pk=category_id).delete()
        messages.success(request, MSG_EQUIPMENT_CATEGORY_DELETED)
        return redirect(to="equipment:get_category")
    return render(request, "equipment_accounting/delete_category.html")


@login_required(login_url='/login/')
def get_equipments(request):
    """
    Render the page with list of equipments

    This function renders a page that displays a list of equipment. It also checks whether
    the user is logged in.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        get_equipments(request)
    """

    check_equipment_booking()

    allowed_positions = PER_CHANGE_EQUIPMENTS
    profile = request.user.profile
    has_permission = profile.user_position.filter(positions_category__in=allowed_positions).exists()

    booking_date = EquipmentBooking.objects.all().order_by("booking_date_from")
    equipments = Equipments.objects.all()
    return render(
                    request,
                    "equipment_accounting/equipment.html",
                    context={
                                "equipments": equipments,
                                "has_permission": has_permission,
                                "booking_date":booking_date
                            }
                )


@login_required(login_url='/login/')
def add_equipment(request):
    """
    Add data of equipment

    This function adds the equipment data to the database. It also checks whether the user is logged
    in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        add_equipment(request)
    """

    permission = permissions_equipment_checker(request)
    if not permission:
        messages.error(request, MSG_ACCESS_DENIED)
        return redirect(to="equipment:get_equipments")

    categories = EquipmentsCategories.objects.all()
    if request.method == "POST":
        form = EquipmentsForm(request.POST, request.FILES)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.save()
            choise_categories_filter = request.POST.getlist("categories")
            choise_categories = EquipmentsCategories.objects.filter(
                                equipment_category_name__in=choise_categories_filter
                                                                    )
            for category in choise_categories:
                equipment.equipment_category.set([category])
            messages.success(request, MSG_EQUIPMENT_ADDED)
            return redirect(to="equipment:get_equipments")

        messages.error(request, MSG_INVALID_DATA)
        context={'form': form, 'categories': categories}
        return render(request, "equipment_accounting/add_equipment.html", context)
    context={'form': EquipmentsForm(), 'categories': categories}
    return render(request, "equipment_accounting/add_equipment.html", context)


@login_required(login_url='/login/')
def detail_equipment(request, equipment_id):
    """
    Rendered the page with data about equipment

    This function renders the page with data about the equipment. It also
    checks whether the user is logged in.
    
    Parameters:
        request (HttpRequest): The HTTP request object.
        equipment_id (int): The ID of the equipment to be show.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        detail_equipment(request, equipment_id)
    """

    permission = permissions_equipment_checker(request)
    equipment = get_object_or_404(Equipments, pk=equipment_id)
    context={'equipment': equipment, "permission":permission}
    return render(request, 'equipment_accounting/detail.html', context)


@login_required(login_url='/login/')
def change_equipment(request, equipment_id):
    """
    Change data of equipment

    This function modifies the equipment data based on the provided equipment ID. It also
    checks whether the user is logged in and has the permissions to perform this action.

    Parameters:
        request (HttpRequest): The HTTP request object.
        equipment_id (int): The ID of the equipment to be change.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        change_equipment(request, equipment_id)
    """

    permission = permissions_equipment_checker(request)
    if not permission:
        messages.error(request, MSG_ACCESS_DENIED)
        return redirect(to="equipment:get_equipments")
    equipment = get_object_or_404(Equipments, pk=equipment_id)
    categories = EquipmentsCategories.objects.all()
    if request.method == "POST":
        form = EquipmentsForm(request.POST, request.FILES, instance=equipment)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.save()
            categories_filter = request.POST.getlist("categories")
            choice_categories = EquipmentsCategories.objects.filter(
                                    equipment_category_name__in=categories_filter
                                                                   )
            for category in choice_categories:
                equipment.equipment_category.set([category])
            messages.success(request, MSG_EQUIPMENT_UPDATED)
            return redirect(to="equipment:get_equipments")

        messages.error(request, MSG_INVALID_DATA)
        context={"form": form, 'categories': categories}
        return render(request, "equipment_accounting/change_equipment.html", context)
    context = {"equipment": equipment, 'categories': categories}
    return render(request, "equipment_accounting/change_equipment.html", context)


@login_required(login_url='/login/')
def delete_equipment(request, equipment_id):
    """
    Delete equipment

    This function deletes data for equipment based on the provided equipment ID. It requires
    the user to be logged in. 

    Parameters:
        request (HttpRequest): The HTTP request object.
        equipment_id (int): The ID of the equipment to be delete.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        delete_equipment(request, equipment_id)
    """
    permission = permissions_equipment_checker(request)
    if not permission:
        messages.error(request, MSG_ACCESS_DENIED)
        return redirect(to="equipment:get_equipments")

    if request.method == "POST":
        Equipments.objects.filter(pk=equipment_id).delete()
        messages.success(request, MSG_EQUIPMENT_DELETED)
        return redirect(to="equipment:get_equipments")
    return render(request, "equipment_accounting/delete_equipment.html")


@login_required(login_url='/login/')
def book_equipment(request, equipment_id):
    """
    Book equipment for a user.

    This function handles the booking of equipment for a user. It requires the user to be
    logged in. It validates the booking form, checks for conflicting bookings, and saves
    the booking record if all validations pass.

    Parameters:
        request (HttpRequest): The HTTP request object.
        equipment_id (int): The ID of the equipment to be booked.

    Returns:
        HttpResponse: The HTTP response object.

    Example:
        book_equipment(request, equipment_id)
    """
    equipment = get_object_or_404(Equipments, pk=equipment_id)
    if request.method == "POST":
        form = BookingEquipmentsForm(request.POST)
        print(form)
        if form.is_valid():
            booking_date_from = form.cleaned_data.get("booking_date_from")
            booking_date_to = form.cleaned_data.get("booking_date_to")
            if booking_date_from and booking_date_to and booking_date_from > booking_date_to:
                messages.error(request, MSG_INVALID_START_DATE)
            elif booking_date_from and booking_date_from < datetime.now().date():
                messages.error(request, MSG_INVALID_END_DATE)
            elif (booking_date_to - booking_date_from).days > 30:
                messages.error(request, MSG_INVALID_BOOKING_DURATION)
            else:

                conflicting_bookings = EquipmentBooking.objects.filter(
                    Q(reserved_equipment=equipment) &
                    (
                        Q(
                            booking_date_from__lte=booking_date_to,
                            booking_date_to__gte=booking_date_from
                        ) | Q(
                                booking_date_from__gte=booking_date_from,
                                booking_date_from__lte=booking_date_to
                             )
                    )
                                                                     )
                if conflicting_bookings.exists():
                    messages.error(request, MSG_INVALID_BOOKING_PERIOD_OVERLAP)
                else:
                    booking = form.save(commit=False)
                    booking.club_member = request.user
                    booking.reserved_equipment = equipment
                    booking.save()
                    messages.success(request, MSG_EQUIPMENT_RESERVED_SUCCESSFULLY)
                    return redirect(to="equipment:get_equipments")
        else:
            context={"form": form}
            return render(request, "equipment_accounting/book_equipment.html", context)
    else:
        form = BookingEquipmentsForm()
    context={"form": form, "equipment": equipment}
    return render(request, "equipment_accounting/book_equipment.html", context)


@login_required(login_url='/login/')
def get_book_equipment(request, equipment_id):
    """
    Render the page displaying booking for a specific equipment

    This function renders the page that displays the bookings made for a specific equipment.
    It requires the user to be logged in and checks the user's permission to access the
    equipment information.

    Parameters:
        request (HttpRequest): The HTTP request object.
        equipment_id (int): The ID of the equipment.

    Returns:
        HttpResponse: The HTTP response containing the rendered page.

    Example:
        get_book_equipment(request, equipment_id)

    """

    permission = permissions_equipment_checker(request)
    equipment = get_object_or_404(Equipments, pk=equipment_id)
    booking_query = EquipmentBooking.objects.filter(reserved_equipment=equipment)
    book_equipment_list = booking_query.order_by('booking_date_from')
    context={
        "book_equipment_list": book_equipment_list,
        "equipment": equipment,
        "permission": permission
        }
    return render(request, "equipment_accounting/get_book_equipment.html",context)


@login_required(login_url='/login/')
def cancel_equipment_reservation(request, book_equipment_id):
    """
    Cancel equipment reservation.

    This function cancels the reservation for a specific equipment booking based on the
    provided booking ID.

    Parameters:
        request (HttpRequest): The HTTP request object.
        book_equipment (int): The ID of the equipment booking to be canceled.

    Returns:
        HttpResponse: A redirect response to the equipment listing page.

    Example:
        cancel_equipment_reservation(request, book_equipment)
    """

    if request.method == "POST":
        EquipmentBooking.objects.filter(pk=book_equipment_id).delete()
        messages.success(request, MSG_BOOKING_PERIOD_DELETED)
        return redirect(to="equipment:get_equipments")
    return render(request, "equipment_accounting/cancel_equipment_reservation.html")


def permissions_equipment_checker(request):
    """
    Check user permissions for equipment management.

    This function checks the permissions of the user associated with the given request
    to determine if they have the necessary rights for equipment management. It verifies
    if the user's profile exists and if any of their positions have the required category
    for changing equipment.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        bool: True - if the user has the necessary permissions, False - otherwise.

    Example:
        has_permissions = permissions_equipment_checker(request)
    """

    permission = True
    try:
        profile = request.user.profile
        user_positions = profile.user_position.all()
    except Profile.DoesNotExist:
        permission = False
        return permission

    allowed_positions = PER_CHANGE_EQUIPMENTS

    if not any(position.positions_category in allowed_positions for position in user_positions):
        permission = False
        return permission

    return permission


def check_equipment_booking():
    """
    Check equipment bookings and delete expired records.

    This function checks the equipment bookings and deletes the records that have a return date
    earlier than the current date (today).

    Parameters:
        None

    Returns:
        None

    Example:
        check_equipment_booking()
    """

    EquipmentBooking.objects.filter(booking_date_to__lt=date.today()).delete()
