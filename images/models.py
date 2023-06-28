from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Image(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='images_created',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    url = models.URLField(max_length=2000)
    images = models.ImageField(upload_to='images/%Y/%m/%d/')
    description = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True)
    users_like = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='images_liked',
        blank=True
    )

    class Meta:
        indexes = [models.Index(fields=['-created']), ]  # индекс базы данных в убывающем порядке
        ordering = ['-created']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """ Автоматически генерировать поля slug
            на основе значения поля title
        """
        if not self.slug:
            self.slu = slugify(self.title)
        super().save(*args, **kwargs)
