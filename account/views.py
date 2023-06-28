from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(  # пользователь аутентифицируется по базе данных методом authenticate()
                request, username=cd['username'], password=cd['password']
            )
            if user is not None:
                if user.is_active:  # статус пользователя проверяется путем обращения к атрибуту is_active
                    print(user.is_active)
                    login(request, user)  # Пользователь задается в сеансе путем вызова метода login()
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required  # проверяет аутентификацию текущего пользователя
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})


def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)  # создать пользователя, но не сохранять его
            new_user.set_password(user_form.cleaned_data['password'])  # В целях безопасности используем метод
            # set_password() данный метод хэширует пароль
            new_user.save()
            Profile.objects.create(user=new_user)  # создаем объект Profile, который расширяет пользовательскую модель
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required  # проверяет аутентификацию текущего пользователя
def edit(request):
    """Редактирование профиля"""
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)

        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(
        request,
        'account/edit.html',
        {'user_form': user_form, 'profile_form': profile_form}
    )