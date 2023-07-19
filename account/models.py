from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings


class Profile(models.Model):
    """Класс пользователя"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'


class Contact(models.Model):
    """ Промежуточная модель для взаимосвязей пользователей"""
    user_form = models.ForeignKey(
        'auth.User',
        related_name='rel_from_set',
        on_delete=models.CASCADE
    )
    user_to = models.ForeignKey(
        'auth.User',
        related_name='rel_to_set',
        on_delete=models.CASCADE
    )

    created = models.DateTimeField('хранение времени взаимосвязи', auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['-created']), ]
        ordering = ['-created']

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'


user_model = get_user_model()  # получаем модель пользователя
# В модель User добавляем поле автоматически
# Метод add_to_class() моделей Django применяется для того, чтобы динамически подправлять модель User
user_model.add_to_class('following', models.ManyToManyField(
    'self',  # Указываем что взаимосвязь многие-ко-многим из модели User на саму себя
    through=Contact,  # указываем что нужно использовать конкретно-прикладную промежуточную модель
    related_name='followers',
    symmetrical=False  # В данном же случае устанавливается параметр symmetrical=False, чтобы определить не336
    # Отслеживание действий пользователя симметричную взаимосвязь (если я на вас подписываюсь, то это не означает,
    # что вы автоматически подписываетесь на меня)
))
