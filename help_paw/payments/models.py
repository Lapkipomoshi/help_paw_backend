from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from shelters.models import Shelter

User = get_user_model()


class YookassaOAuthToken(models.Model):
    """OAuth токен для создания платежей от имени приюта"""
    shelter = models.ForeignKey(
        Shelter,
        verbose_name='Приют',
        on_delete=models.CASCADE,
        related_name='yookassa_token')
    token = models.CharField('Токен', max_length=255)
    expires_at = models.DateTimeField('Дата истекания')

    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class Payment(models.Model):
    """Данные о платеже"""
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
        null=True
    )
    amount = models.FloatField('Сумма', validators=[MinValueValidator(1.0)])
    is_successful = models.BooleanField('Завершен успешно', default=False)
    external_id = models.CharField('Внешний ID платежа', max_length=255, unique=True)
