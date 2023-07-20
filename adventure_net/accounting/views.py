from django.contrib import messages
from django.contrib.auth import decorators
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CategoryOperationForm, TypeOperationForm, ClubTreasuryForm
from .models import OperationType, OperationCategory, ClubTreasury
from adventure_net.messages import MSG_WELCOME, MSG_AMOUNT_ADDED, MSG_INVALID_DATA, MSG_CAT_OPERATION_ADDED,\
    MSG_TYPE_OPERATION_ADDED, MSG_ACCESS_DENIED
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


def chenge_club_treasury(request):
    return render(request, 'users/placeholders.html', context={"msg": MSG_WELCOME})


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


def chenge_operation_category(request):
    return render(request, 'users/placeholders.html', context={"msg": MSG_WELCOME})


def delete_operation_category(request):
    return render(request, 'users/placeholders.html', context={"msg": MSG_WELCOME})


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
    

def chenge_operation_type(request):
    return render(request, 'users/placeholders.html', context={"msg": MSG_WELCOME})


def delete_operation_type(request):
    return render(request, 'users/placeholders.html', context={"msg": MSG_WELCOME})


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
