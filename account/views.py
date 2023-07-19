from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST

from actions.models import Action
from actions.utils import create_action
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from .models import Contact


def user_login(request):
    """ Вход в учётку пользователя
        Не используется, как пример
    """
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
    actions = Action.objects.exclude(user=request.user)  # получаем все действия кроме пользователя
    following_ids = request.user.following.values_list('id', flat=True)  # проверяем подписал ли пользователь на кого-то

    if following_ids:  # Если пользователь подписан на других, то извлекаем только их действия
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]
    return render(
        request,
        'account/dashboard.html',
        {'section': 'dashboard', 'actions': actions}
    )


def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)  # создать пользователя, но не сохранять его
            new_user.set_password(user_form.cleaned_data['password'])  # В целях безопасности используем метод
            # set_password() данный метод хэширует пароль
            new_user.save()
            Profile.objects.create(user=new_user)  # создаем объект Profile, который расширяет пользовательскую модель
            create_action(new_user, 'has created an account')  # вызываем функцию(собственно написанную) для
            # добавления действий
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


@login_required
def user_list(request):
    """Список активных пользователей"""
    users = User.objects.filter(is_active=True)
    return render(
        request,
        'account/user/list.html',
        {'section': 'people', 'users': users}
    )


@login_required
def user_detail(request, username):
    """Детальная информация об пользователе"""
    user = get_object_or_404(User, username=username, is_active=True)
    return render(
        request,
        'account/user/detail.html',
        {'section': 'people', 'user': user}
    )


@require_POST
@login_required
def user_follow(request):
    """Создание подписок на пользователей"""
    user_id = request.POST.get('id')  # получаем пользователя
    action = request.POST.get('action')  # получаем действие
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':  # если действие подписаться, используем промежуточную модель для создания подписки
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user
                )
                create_action(request.user, 'is_following', user)  # вызываем функцию(собственно написанную) для
            # добавления действий
            else:  # в остальных случаях мы отписываемся
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
