from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Пользователи проекта с ролями:
        Владелец приюта,
        Волонтер приюта,
        Модератор контента,
        Администратор
    """

    SHELTER_OWNER = 'shelter_owner'
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (SHELTER_OWNER, 'Владелец приюта'),
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор контента')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    username = models.CharField(
        'Имя пользователя',
        unique=False,
        max_length=150,
        help_text='Введите имя пользователя',
    )

    status = models.CharField(
        'Статус',
        help_text='Выберите статус пользователя',
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER
    )
    subscription_pet = models.ManyToManyField(
        'shelters.Pet',
        verbose_name='Подписка на животное',
        related_name='subscribers',
        blank=True,
        through='UserPet'
    )
    subscription_shelter = models.ManyToManyField(
        'shelters.Shelter',
        verbose_name='Подписка на приют',
        related_name='subscribers',
        blank=True,
        through='UserShelter'
    )

    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        max_length=254,
        null=False
    )
    donations_sum = models.DecimalField(
        'Сумма пожертвований',
        max_digits=8,
        decimal_places=2,
        default=0
    )

    @property
    def is_admin(self):
        return self.status == self.ADMIN

    @property
    def is_moderator(self):
        return self.status == self.MODERATOR

    @property
    def is_shelter_owner(self):
        return self.status == self.SHELTER_OWNER

    @property
    def is_user(self):
        return self.status == self.USER

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class UserPet(models.Model):
    pet_subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    pet = models.ForeignKey(
        'shelters.Pet',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.pet_subscriber} следит за судьбой: {self.pet}'


class UserShelter(models.Model):
    shelter_subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    shelter = models.ForeignKey(
        'shelters.Shelter',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.shelter_subscriber} подписан на приют: {self.shelter}'
