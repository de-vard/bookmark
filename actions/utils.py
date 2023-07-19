import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Action


def create_action(user, verb, target=None):
    # user это пользователь, verb это строка описывающая действие, target это объект модели Django
    """Добавляет действия в модель активности"""
    now = timezone.now()  # берется текущее время
    last_minute = now - datetime.timedelta(seconds=60)  # отнимаем минуту
    similar_actions = Action.objects.filter(  # получения действий

        user_id=user.id,
        verb=verb,
        created__gte=last_minute
    )
    if target:  # Если передан target, то запрос к базе данных дополнительно фильтруется по типу и идентификатору цели
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(
            target_ct=target_ct,
            target_id=target.id
        )
    if not similar_actions:  # если за последнюю минуту не было идентичного действия, то создается объект Action
        action = Action(user=user, verb=verb, target=target)
        action.save()
        return True
    return False
