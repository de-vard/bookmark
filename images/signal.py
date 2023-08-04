from django.db.models.signals import m2m_changed
from django.dispatch import receiver  # Эта функция используется для регистрации обработчика сигнала.
from .models import Image


@receiver(m2m_changed, sender=Image.users_like.through)
def users_like_changed(sender, instance, **kwargs):
    """ Функция вызывается при изменении связи
         многие-ко-многим (many-to-many, m2m)
         между моделями Image и users_like
    """
    # instance - это экземпляр модели
    instance.total_likes = instance.users_like.count()  # вычисляется значение поля total_likes
    instance.save()
