from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, decorators
from django.contrib import messages
from .forms import RegisterForm, LoginForm


def main(request):
    return render(request, 'users/main.html', context={"msg": "Good news!!! It is working)"})


def signup_user(request):
    if request.user.is_authenticated:
        return redirect(to="users:main")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to="users:main")
        else:
            return render(request, 'users/singup.html', context={'form': form})
    return render(request, 'users/singup.html', context={'form': RegisterForm()})


def login_user(request):
    if request.user.is_authenticated:
        return redirect(to="users:main")

    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is None:
            messages.error(request, 'Username or password did\'t match')
            return redirect(to='users:login')
        login(request, user)
        return redirect(to="users:main")
    return render(request, 'users/login.html', context={'form': LoginForm()})


@decorators.login_required
def logout_user(request):
    logout(request)
    return redirect(to="users:main")