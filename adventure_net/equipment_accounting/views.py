from datetime import datetime, date

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F

from .forms import EquipmentsForm, EquipmentsCategoriesForm, BookingEquipmentsForm
from .models import Equipments, EquipmentsCategories, EquipmentBooking
from users.models import Profile
from adventure_net.messages import MSG_WELCOME, MSG_INVALID_DATA, MSG_ACCESS_DENIED,\
    MSG_EQUIPMENT_CATEGORY_ADDED, MSG_EQUIPMENT_CATEGORY_UPDATED, MSG_EQUIPMENT_CATEGORY_DELETED,\
    MSG_EQUIPMENT_ADDED, MSG_EQUIPMENT_UPDATED, MSG_EQUIPMENT_DELETED, MSG_INVALID_START_DATE,\
    MSG_INVALID_END_DATE, MSG_INVALID_BOOKING_DURATION, MSG_INVALID_BOOKING_PERIOD_OVERLAP,\
    MSG_EQUIPMENT_RESERVED_SUCCESSFULLY, MSG_BOOKING_PERIOD_DELETED
    

@login_required(login_url='/login/')
def checker(request):
    return render(
        request,
        "equipment_accounting/checker.html",
        context={"msg": MSG_WELCOME},
    )


@login_required(login_url='/login/')
def get_category(request):
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
        else:
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
        else:
            messages.error(request, MSG_INVALID_DATA)
            return render(
                request, "equipment_accounting/change_category.html", context={"form": form}
            )
    return render(request, "equipment_accounting/change_category.html", context={"category": category})


@login_required(login_url='/login/')
def delete_category(request, category_id):
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
    check_equipment_booking(request)

    allowed_positions = ["Equipment manager", "Head"] #### Винести в окремий файл
    profile = request.user.profile
    has_permission = profile.user_position.filter(positions_category__in=allowed_positions).exists()

    booking_date = EquipmentBooking.objects.all().order_by("booking_date_from")
    equipments = Equipments.objects.all()
    return render(
                    request,
                    "equipment_accounting/equipment.html",
                    context={"equipments": equipments, "has_permission": has_permission, "booking_date":booking_date}
                )


@login_required(login_url='/login/')
def add_equipment(request):
    permission = permissions_equipment_checker(request)
    if not permission:
        return redirect(to="equipment:get_equipments")
    
    categories = EquipmentsCategories.objects.all()
    if request.method == "POST":
        form = EquipmentsForm(request.POST, request.FILES)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.save()
            choise_categories = EquipmentsCategories.objects.filter(equipment_category_name__in=request.POST.getlist("categories"))
            for category in choise_categories:
                equipment.equipment_category.set([category])
            messages.success(request, MSG_EQUIPMENT_ADDED)
            return redirect(to="equipment:get_equipments")
        else:
            messages.error(request, MSG_INVALID_DATA)
            return render(request, "equipment_accounting/add_equipment.html", context={'form': form, 'categories': categories})
    return render(request, "equipment_accounting/add_equipment.html", context={'form': EquipmentsForm(), 'categories': categories})


@login_required(login_url='/login/')
def detail_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipments, pk=equipment_id)
    return render(request, 'equipment_accounting/detail.html', context={'equipment': equipment})


@login_required(login_url='/login/')
def change_equipment(request, equipment_id):
    permission = permissions_equipment_checker(request)
    if not permission:
        return redirect(to="equipment:get_equipments")
    
    equipment = get_object_or_404(Equipments, pk=equipment_id)
    categories = EquipmentsCategories.objects.all()
    if request.method == "POST":
        form = EquipmentsForm(request.POST, request.FILES, instance=equipment)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.save()
            choise_categories = EquipmentsCategories.objects.filter(equipment_category_name__in=request.POST.getlist("categories"))
            for category in choise_categories:
                equipment.equipment_category.set([category])
            messages.success(request, MSG_EQUIPMENT_UPDATED)
            return redirect(to="equipment:get_equipments")
        else:
            messages.error(request, MSG_INVALID_DATA)
            return render(
                request, "equipment_accounting/change_equipment.html", context={"form": form, 'categories': categories}
            )
    return render(request, "equipment_accounting/change_equipment.html", context={"equipment": equipment, 'categories': categories})

@login_required(login_url='/login/')
def delete_equipment(request, equipment_id):
    permission = permissions_equipment_checker(request)
    if not permission:
        return redirect(to="equipment:get_equipments")
    
    if request.method == "POST":
        Equipments.objects.filter(pk=equipment_id).delete()
        messages.success(request, MSG_EQUIPMENT_DELETED)
        return redirect(to="equipment:get_equipments")
    return render(request, "equipment_accounting/delete_equipment.html")


@login_required(login_url='/login/')
def book_equipment(request, equipment_id):
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
                        Q(booking_date_from__lte=booking_date_to, booking_date_to__gte=booking_date_from)
                        | Q(booking_date_from__gte=booking_date_from, booking_date_from__lte=booking_date_to)
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
            return render(request, "equipment_accounting/book_equipment.html", context={"form": form})
    else:
        form = BookingEquipmentsForm()
    return render(
        request,
        "equipment_accounting/book_equipment.html",
        context={"form": form, "equipment": equipment}
    )


@login_required(login_url='/login/')
def get_book_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipments, pk=equipment_id)
    book_equipments = EquipmentBooking.objects.filter(reserved_equipment=equipment).order_by('booking_date_from')
    return render(
        request,
        "equipment_accounting/get_book_equipment.html",
        context={"book_equipments": book_equipments, "equipment": equipment}
    )

@login_required(login_url='/login/')
def cancel_equipment_reservation(request, book_equipment):
    if request.method == "POST":
        EquipmentBooking.objects.filter(pk=book_equipment).delete()
        messages.success(request, MSG_BOOKING_PERIOD_DELETED)
        return redirect(to="equipment:get_equipments")
    return render(request, "equipment_accounting/cancel_equipment_reservation.html")


def permissions_equipment_checker(request):
    permission = True
    try:
        profile = request.user.profile
        user_positions = profile.user_position.all()
    except Profile.DoesNotExist:
        permission = False
        return permission

    allowed_positions = ["Equipment manager", "Head"] #### Винести в окремий файл

    if not any(position.positions_category in allowed_positions for position in user_positions):
        messages.error(request, MSG_ACCESS_DENIED)
        permission = False
        return permission
    else:
        return permission


def check_equipment_booking(request):
    EquipmentBooking.objects.filter(booking_date_to__lt=date.today()).delete()


