from django import forms
from django.core.files.base import ContentFile
from django.utils.text import slugify

from .models import Image
import requests


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'url', 'description']
        widgets = {
            'url': forms.HiddenInput,  # виджет прорисовывается как HTML-элемент input с атрибутом type="hidden"
            # используем данный виджет, чтобы это поле было не видимым для пользователя
        }

    def clean_url(self):
        """Проверка на расширение файла, является ли оно изображением"""
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg', 'png']
        extension = url.rsplit('.', 1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError('The given URL does not match valid image extensions.')
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        """Переопределим метод save, чтобы получать файл изображения по URL-адресу и сохранить его в файловой системе"""
        image = super().save(commit=False)  # экземпляр изображения создаем путем вызова метода save() с commit=False.
        image_url = self.cleaned_data['url']  # URL-адрес изображения извлекается из словаря clean_data
        name = slugify(image.title)
        extension = image_url.rsplit('.', 1)[1].lower()
        image_name = f"{name}.{extension}"  # имя изображения формируется названием изображения с расширением файла
        response = requests.get(image_url)  # Библиотека requests используется для скачивания изображения
        image.image.save(image_name, ContentFile(response.content), save=False)
        if commit:  # форма сохраняется в базе данных только в том случае, если параметр commit равен True
            image.save()
        return image
