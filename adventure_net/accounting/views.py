from django.contrib import messages
from django.contrib.auth import decorators
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CategoryOperationForm, TypeOperationForm, ClubTreasuryForm
from .models import OperationType, OperationCategory, ClubTreasury
from adventure_net.messages import MSG_WELCOME, MSG_AMOUNT_ADDED, MSG_INVALID_DATA, MSG_CAT_OPERATION_ADDED,\
    MSG_TYPE_OPERATION_ADDED, MSG_ACCESS_DENIED, MSG_TYPE_OPERATION_DELETE, MSG_CAT_OPERATION_DELETE, \
    MSG_TYPE_OPERATION_CHENGE, MSG_CAT_OPERATION_CHENGE, MSG_AMOUNT_CHANGE, MSG_CAT_OPERATION_DELETE_ERR, \
    MSG_TYPE_OPERATION_DELETE_ERR
from users.models import Profile
from adventure_net.permissions import PER_CHANGE_AMOUNT


@decorators.login_required(login_url='/login/')
def add_club_treasury(request):
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
    permission = permissions_checker(request)

    treasuries = ClubTreasury.objects.all()

    return render(
        request,
        "accounting/get_club_treasury.html",
        context={"treasuries": treasuries, "permission":permission}
    )


@decorators.login_required(login_url='/login/')
def chenge_club_treasury(request, treasury_id):
    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")
    
    current_record = get_object_or_404(ClubTreasury, pk=treasury_id)
    if request.method == "POST":
        form = ClubTreasuryForm(request.POST, instance=current_record)

        if form.is_valid():
            form.save()
            messages.success(request, MSG_AMOUNT_CHANGE)
            return redirect(to="accounting:get_club_treasury")
        
        messages.error(request, MSG_INVALID_DATA)
        return render(request, "accounting/chenge_club_treasury.html", context={"form": form, "current_record": current_record})
    form = ClubTreasuryForm(instance=current_record)
    return render(request, "accounting/chenge_club_treasury.html", context={"form": form, "current_record": current_record})


@decorators.login_required(login_url='/login/')
def add_operation_category(request):
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
def chenge_operation_category(request, operation_category_id):
    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")
    
    current_operation_category = get_object_or_404(OperationCategory, pk=operation_category_id)
    if request.method == "POST":
        form = CategoryOperationForm(request.POST, instance=current_operation_category)

        if form.is_valid():
            new_category_name = form.cleaned_data["category_name"]

            if OperationCategory.objects.filter(category_name=new_category_name).exclude(pk=operation_category_id).exists():
                return render(request, "accounting/change_operation_category.html", context={"form": form, "current_operation_category": current_operation_category})

            form.save()
            messages.success(request, MSG_CAT_OPERATION_CHENGE)
            return redirect(to="accounting:get_operation_category")

        messages.error(request, MSG_INVALID_DATA)
        return render(request, "accounting/change_operation_category.html", context={"form": form, "current_operation_category": current_operation_category})

    form = CategoryOperationForm(instance=current_operation_category)
    return render(request, "accounting/change_operation_category.html", context={"form": form, "current_operation_category": current_operation_category})


@decorators.login_required(login_url='/login/')
def delete_operation_category(request, operation_category_id):
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
def chenge_operation_type(request, operation_type_id):
    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")

    operation_type = get_object_or_404(OperationType, pk=operation_type_id)

    if request.method == "POST":
        form = TypeOperationForm(request.POST, instance=operation_type)

        if form.is_valid():
            new_type_name = form.cleaned_data["type_name"]
            if OperationType.objects.filter(type_name=new_type_name).exclude(pk=operation_type_id).exists():
                return render(request, "accounting/change_operation_type.html", context={"form": form, "operation_type": operation_type})

            form.save()
            messages.success(request, MSG_TYPE_OPERATION_CHENGE)
            return redirect(to="accounting:get_operation_type")

        messages.error(request, MSG_INVALID_DATA)
        return render(request, "accounting/change_operation_type.html", context={"form": form, "operation_type": operation_type})

    form = TypeOperationForm(instance=operation_type)
    return render(request, "accounting/change_operation_type.html", context={"form": form, "operation_type": operation_type})


@decorators.login_required(login_url='/login/')
def delete_operation_type(request, operation_type_id):
    permission = permissions_checker(request)
    if not permission:
        return redirect(to="accounting:get_club_treasury")
    
    operation_type = get_object_or_404(OperationType, pk=operation_type_id)
    if request.method == "POST":
        if ClubTreasury.objects.filter(operation_type=operation_type).exists():
            messages.error(request, MSG_TYPE_OPERATION_DELETE_ERR)
            return redirect(to="accounting:get_operation_category")
        operation_type.delete()
        messages.success(request, MSG_TYPE_OPERATION_DELETE)
        return redirect(to="accounting:get_operation_type")
    return render(request, "accounting/delete_operation_type.html")


def permissions_checker(request):
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
