from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


def signup_user(request):
    if request.user.is_authenticated:
        return redirect(to="equipment:get_equipments") # ЗАМІНИТИ НА ГОЛОВНУ СТОРІНКУ

    return render(request, )


