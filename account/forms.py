from django import forms
from django.contrib.auth.models import User
from .models import Profile


class LoginForm(forms.Form):
    """Форма входа"""
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    """Регистрация пользователя"""
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']

    def clean_password2(self):
        """Проверка паролей на соответствие"""
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_email(self):
        """ Проверка email адресов на уникальность """
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data


class UserEditForm(forms.ModelForm):  # Две формы (UserEditForm ProfileEditForm) так как у пользователя две бд
    # связанные один к одному
    """Редактирование встроенной в Django модели User"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileEditForm(forms.ModelForm):  # Две формы (UserEditForm ProfileEditForm) так как у пользователя две бд
    # связанные один к одному
    """Редактирование данные профиля, модели Profile"""

    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']
