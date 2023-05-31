from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm


def signup_user(request):
    if request.user.is_authenticated:
        return redirect(to="equipment:get_equipments") # ЗАМІНИТИ НА ГОЛОВНУ СТОРІНКУ

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to="equipment:get_equipments") # ЗАМІНИТИ НА ГОЛОВНУ СТОРІНКУ
        else:
            return render(request, 'users/singup.html', context={'form': form})
    return render(request, 'users/singup.html', context={'form': RegisterForm()})


