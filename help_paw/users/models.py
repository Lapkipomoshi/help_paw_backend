from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Пользователи проекта с ролями:
        Аноним,
        Аутентифицированный пользователь,
        Владелец приюта,
        Волонтер приюта,
        Модератор контента,
        Администратор
    """

    USER = 'user'
    SHELTER_OWNER = 'shelre_owner'
    VOLUNTEER = 'volunteer'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'Аутентифицированный пользователь'),
        (SHELTER_OWNER, 'shelre_owner'),
        (VOLUNTEER, 'volunteer')
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор контента')
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        help_text='Введите имя пользователя',
        max_length=150,
        null=False,
        unique=True
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        help_text='Введите адрес эл. почты',
        unique=True,
        max_length=254
    )
    status = models.CharField(
        verbose_name='Статус',
        help_text='Выберите статус пользователя',
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_shelter_owner(self):
        return self.role == self.SHELTER_OWNER

    @property
    def is_volunteer(self):
        return self.role == self.VOLUNTEER

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
