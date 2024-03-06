from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from shelters.models import Shelter

User = get_user_model()


class YookassaOAuthToken(models.Model):
    """OAuth токен для создания платежей от имени приюта"""
    shelter = models.OneToOneField(
        Shelter,
        verbose_name='Приют',
        on_delete=models.CASCADE,
        related_name='yookassa_token')
    token = models.CharField('Токен', max_length=512)
    expires_at = models.DateTimeField('Дата истечения')

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    class Meta:
        verbose_name = 'OAuth токен приюта'
        verbose_name_plural = 'OAuth токены приютов'

    def __str__(self):
        return self.shelter.name


class Donation(models.Model):
    """Данные о пожертвовании"""
    shelter = models.ForeignKey(
        Shelter,
        verbose_name='Приют',
        on_delete=models.SET_NULL,
        related_name='payments',
        null=True
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.SET_NULL,
        related_name='payments',
        null=True,
        blank=True,
        default=None
    )
    amount = models.DecimalField(
        'Сумма',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(1.0)]
    )
    is_successful = models.BooleanField(
        'Завершен успешно',
        default=False
    )
    external_id = models.CharField(
        'Внешний ID платежа',
        max_length=255,
        unique=True
    )
    created_at = models.DateTimeField('Дата и время создания платежа')

    class Meta:
        verbose_name = 'Пожертвование'
        verbose_name_plural = 'Пожертвования'

    def __str__(self):
        return f'{self.user} -> {self.shelter.name} сумма: {self.amount}'
