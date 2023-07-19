from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from .forms import ImageCreateForm
from .models import Image
from actions.utils import create_action
import redis
from django.conf import settings

# соединить с redis
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)


@login_required  # предотвращать доступ не аутентифицированных пользователей
def image_create(request):
    """Создание изображения"""
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            messages.success(request, 'Image added successfully')
            return redirect(new_image.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)
    return render(
        request,
        'images/image/create.html',
        {'section': 'images', 'form': form}
    )


def image_detail(request, id, slug):
    """Детальное рассмотрение изображения"""
    image = get_object_or_404(Image, id=id, slug=slug)
    total_views = r.incr(f'image:{image.id}:views')  # увеличить общее число просмотров изображения на 1
    r.zincrby('image_ranking', 1, image.id)  # Команда zincrby() используется для сохранения просмотров изображений в
    # сортированном множестве
    return render(
        request,
        'images/image/detail.html',
        {'selction': 'image', 'image': image, 'total_views': total_views}
    )


@login_required
def image_ranking(request):
    """Отображение рейтинга наиболее просматриваемых изображений"""
    image_ranking = r.zrange('image_ranking', 0, -1,desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(
        request,
        'images/image/ranking.html',
        {'section': 'images','most_viewed': most_viewed}
    )


@login_required  # проверка пользователя на регистрацию
@require_POST  # разрешаются запросы только методом POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == "like":
                image.users_like.add(request.user)  # метод add добавляет объект
                create_action(request.user, 'likes', image)  # вызываем функцию(собственно написанную) для добавления
                # действий
            else:
                image.users_like.remove(request.user)  # метод remove удаляет объект
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    """Список фотографий"""
    images = Image.objects.all().order_by('-total_likes')  # Получаем все объекты и сортируем по лайкам
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом,
        # то доставить первую страницу
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            # Если AJAX-запрос и страница вне диапазона,
            # то вернуть пустую страницу
            return HttpResponse('')
        # Если страница вне диапазона,
        # то вернуть последнюю страницу результатов
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(request,
                      'images/image/list_images.html',
                      {'section': 'images',
                       'images': images})
    return render(request,
                  'images/image/list.html',
                  {'section': 'images',
                   'images': images})


@login_required
def image_create(request):
    """Создание картинки"""
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_image = form.save(commit=False)  # создаем, но не сохраняем
            new_image.user = request.user  # добавляем пользователя
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)  # вызываем функцию(собственно написанную) для
            # добавления действий
            messages.success(request, 'Image added successfully')  # выводим сообщение
            return redirect(new_image.get_absolute_url())  # перенаправляем сразу же на созданный элемент
    else:
        form = ImageCreateForm(data=request.GET)  # вывести форму со старыми данными
    return render(
        request,
        'images/image/create.html',
        {'section': 'images', 'form': form}
    )
