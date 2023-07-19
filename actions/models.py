from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Action(models.Model):
    """
        Модель для хранения действий пользователя

        Django автоматически заполняет поля target_ct и target_id в модели Action на основе типа содержимого и
        первичного ключа объекта цели. Это происходит благодаря использованию класса GenericForeignKey, который
        позволяет создавать общие отношения с любой другой моделью.
    """
    user = models.ForeignKey(
        'auth.User',
        related_name='actions',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    verb = models.CharField('действие которое выполнил пользователь', max_length=255)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания действия')
    target_ct = models.ForeignKey(  # сообщает о модели, используемой для взаимосвязи
        ContentType,
        blank=True,
        null=True,
        related_name='target_obj',
        on_delete=models.CASCADE
    )
    target_id = models.PositiveIntegerField(null=True, blank=True)  # хранения первичного ключа связанного объекта
    target = GenericForeignKey('target_ct', 'target_id')  # GenericForeignKey - это специальный тип поля ForeignKey,

    # который позволяет создавать «универсальные» отношения с любой другой моделью

    class Meta:
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['target_ct', 'target_id']),
        ]
        ordering = ['-created']
