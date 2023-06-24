from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, decorators
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from .forms import RegisterForm, LoginForm, CategoryForm, MembersForm, UpdateAccountInformationForm
from .models import Profile, UserPositions


def main(request):
    return render(request, 'users/main.html', context={"msg": "Good news!!! It is working)"})

def placeholders(request):
    return render(request, 'users/placeholders.html', context={"msg": "This webpage is under development.\
                                                                We apologize for any inconvenience. Please\
                                                                check back later to access the updated version."})
 

def signup_user(request):
    permission = permissions_signup_checker(request)
    if not permission:
        return redirect(to="users:club_members")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Вітаємо! Користувача успішно створено.")
            return redirect(to="users:main")
        else:
            messages.error(request, "Будь ласка введіть коректні дані. ")
            return render(request, 'users/singup.html', context={'form': form})
    return render(request, 'users/singup.html', context={'form': RegisterForm()})


def login_user(request):
    if request.user.is_authenticated:
        return redirect(to="users:main")

    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is None:
            messages.error(request, 'Введено неправильне ім\'я користувача або пароль!')
            return redirect(to='users:login')
        login(request, user)
        messages.success(request, "Вітаємо в турклубі!")
        return redirect(to="users:main")
    return render(request, 'users/login.html', context={'form': LoginForm()})


@decorators.login_required
def logout_user(request):
    logout(request)
    return redirect(to="users:main")


@decorators.login_required(login_url='/login/')
def profile_user(request, user_id):
    allowed_positions = ["Head"] #### Винести в окремий файл
    profile = request.user.profile
    has_permission = profile.user_position.filter(positions_category__in=allowed_positions).exists()

    user_profile = get_object_or_404(Profile, user_id=user_id)
    user_login = user_profile.user.username
    return render(request, 'users/profile.html', context={'users': user_profile, 'login': user_login, 'has_permission':has_permission})


@decorators.login_required(login_url='/login/')
def get_users(request):
    allowed_positions = ["Head"] #### Винести в окремий файл
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
    member = get_object_or_404(Profile, pk=user_id)

    allowed_positions = ["Head"] #### Винести в окремий файл
    profile = request.user.profile
    has_permission = profile.user_position.filter(positions_category__in=allowed_positions).exists()

    if member.user != request.user and not has_permission:
        messages.error(request, 'Ви не маєте прав доступу до цієї сторінки')
        return redirect(to='users:club_members')

    if request.method == "POST":
        form = MembersForm(request.POST or None, request.FILES or None, instance=member)

        # form = MembersForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Дані корисувача успішно змінені")
            return redirect('users:club_members')
    else:
        messages.error(request, "Будь ласка введіть коректні дані. ")
        form = MembersForm(instance=member)
    return render(
                request,
                'users/change_profile.html',
                context={'form': form, 'member': member, "has_permission":has_permission}
                )


@decorators.login_required(login_url='/login/')
def delete_profile(request, user_id):
    permission = permissions_signup_checker(request)
    if not permission:
        return redirect(to="users:club_members")
    
    if request.method == "POST":
        member = get_object_or_404(Profile, pk=user_id)
        user = member.user

        User.objects.filter(pk = user.id).delete()
        messages.success(request, "Дані корисувача успішно видалені")
        return redirect(to="users:club_members")
    return render(request, "users/delete_user.html")



@decorators.login_required(login_url='/login/')
def get_user_position(request):
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
    permission = permissions_signup_checker(request)
    if not permission:
        return redirect(to="users:club_members")
    
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Вітаємо! Позицію члена клуба додано")
            return redirect(to='users:get_user_position')
        else:
            messages.error(request, "Будь ласка введіть коректні дані. ")
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
    permission = permissions_signup_checker(request)
    if not permission:
        return redirect(to="users:club_members")
    
    user_position = get_object_or_404(UserPositions, pk=position_id)
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid() and user_position.positions_category != request.POST["positions_category"]:
            UserPositions.objects.filter(pk=position_id).update(
                positions_category=request.POST["positions_category"],
                positions_category_info=request.POST["positions_category_info"]
            )
            return redirect(to="users:get_user_position")
        if user_position.positions_category == request.POST["positions_category"]:
            UserPositions.objects.filter(pk=position_id).update(
                positions_category_info=request.POST["positions_category_info"]
            )
            messages.success(request, "Вітаємо! Позицію члена клуба змінено")
            return redirect(to="users:get_user_position")
        else:
            messages.error(request, "Будь ласка введіть коректні дані. ")
            return render(
                request,
                "users/change_user_position.html",
                context={"form": form, "user_position": user_position, "position_id": position_id},
            )
    else:
        form = CategoryForm(instance=user_position)
    return render(request, "users/change_user_position.html", context={"form": form, "user_position": user_position})


@decorators.login_required(login_url='/login/')
def delete_user_position(request, position_id):
    permission = permissions_signup_checker(request)
    if not permission:
        return redirect(to="users:club_members")
    
    if request.method == "POST":
        UserPositions.objects.filter(pk = position_id).delete()
        messages.success(request, "Вітаємо! Позицію члена клуба видалено")
        return redirect(to="users:get_user_position")
    return render(request, "users/delete_user_position.html")


@decorators.login_required(login_url='/login/')
def update_account_information(request, user_id):
    member = get_object_or_404(Profile, pk=user_id)

    if member.user != request.user:
        messages.error(request, 'Ви не маєте прав доступу до цієї сторінки')
        return redirect(to='users:club_members')

    user = member.user  # Отримуємо користувача з профілю

    if request.method == "POST":
        form = UpdateAccountInformationForm(request.POST, instance=user)
        if form.is_valid():
            user.username = form.cleaned_data['username']  # Оновлюємо поле логіну
            user.set_password(form.cleaned_data['password'])  # Оновлюємо пароль
            user.save()
            messages.success(request, 'Логін та пароль успішно оновлені.')
            return redirect('users:club_members')
        else:
            messages.error(request, 'Будь ласка, виправте помилки у формі.')
    else:
        form = UpdateAccountInformationForm(instance=user)

    return render(
        request,
        'users/update_account_information.html',
        context={'form': form, 'member': member}
    )






def permissions_signup_checker(request):
    permission = True
    try:
        profile = request.user.profile
        user_positions = profile.user_position.all()
    except Profile.DoesNotExist:
        permission = False
        return permission

    allowed_positions = ["Head"] #### Винести в окремий файл

    if not any(position.positions_category in allowed_positions for position in user_positions):
        messages.error(request, "Ви не маєте прав доступу до цієї сторінки") ###################################
        permission = False
        return permission
    else:
        return permission
