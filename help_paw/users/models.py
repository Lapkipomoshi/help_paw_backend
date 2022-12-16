from django.contrib.auth.models import AbstractUser
from django.db import models

from shelters.models import Pet


class User(AbstractUser):
    """ Пользователи проекта с ролями:
        Владелец приюта,
        Волонтер приюта,
        Модератор контента,
        Администратор
    """

    ROLE_CHOICES = (
        ('SHELTER_OWNER', 'shelre_owner'),
        ('VOLUNTEER', 'volunteer')
        ('ADMIN', 'Администратор'),
        ('MODERATOR', 'Модератор контента')
    )

    status = models.CharField(
        verbose_name='Статус',
        help_text='Выберите статус пользователя',
        max_length=50,
        choices=ROLE_CHOICES,
        default=None
    )
    subscription = models.ManyToManyField(
        Pet,
        verbose_name='Подписка на животное',
        related_name='user',
        blank=True,
        through='UserPet',
        through_fields=('user', 'pet')
    )

    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    @property
    def is_moderator(self):
        return self.role == 'MODERATOR'

    @property
    def is_shelter_owner(self):
        return self.role == 'SHELTER_OWNER'

    @property
    def is_volunteer(self):
        return self.role == 'VOLUNTEER'

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class UserPet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    pet = models.ForeignKey(
        Pet,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    want_to_adopt = models.BooleanField(
        verbose_name='Хочу приютить',
        default=False
    )

    def __str__(self):
        return f'{self.user} следит за судьбой: {self.animal}'
