from django.contrib.auth.models import User
from account.models import Profile


class EmailAuthBackend:
    """Аутентифицировать посредством адреса электронной почты."""

    def authenticate(self, request, username=None, password=None):
        """Возвращает объект user, соответствующий этим учетным данным, либо None"""
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):  # метод check_password() проверяет пароль
                return user
            return None
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    def get_user(self, user_id):
        """Принимает ИД пользователя в качестве параметра и возвращает объект user """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def create_profile(backend, user, *args, **kwargs):
    """Создавать профиль пользователя для социальной аутентификации"""
    Profile.objects.get_or_create(user=user)
