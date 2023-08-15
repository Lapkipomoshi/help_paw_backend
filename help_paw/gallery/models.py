from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from info.models import News

MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_IMAGE_CNT = 5


def validate_image_size(value):
    if value.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            f'Размер изображения не должен превышать {MAX_IMAGE_SIZE} МБ')


class Image(models.Model):
    image = models.ImageField('Изображение', validators=[validate_image_size])

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


@receiver(m2m_changed, sender=News.gallery.through)
def validate_gallery(sender, instance, action, *args, **kwargs):
    if action == 'post_add' and instance.gallery.all().count() > MAX_IMAGE_CNT:
        raise ValidationError(
            f'Максимальное количество изображений в галерее - {MAX_IMAGE_CNT}'
        )
