from datetime import date
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

User = get_user_model()


class ApprovedSheltersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_approved=True)


class Pet(models.Model):
    """Карточка животного."""
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'
    SEX_CHOICE = (
        (MALE, 'самец'),
        (FEMALE, 'самка'),
        (OTHER, 'другое'),
    )
    name = models.CharField('Кличка животного', max_length=100)
    animal_type = models.ForeignKey(
        'AnimalType',
        verbose_name='Вид животного',
        related_name='pets',
        on_delete=models.PROTECT
    )
    sex = models.CharField(
        'Пол животного',
        max_length=6,
        choices=SEX_CHOICE,
        default=OTHER
    )
    birth_date = models.DateField(null=True, blank=True)
    about = models.TextField('Описание животного', max_length=500)
    gallery = models.ManyToManyField(
        'gallery.Image',
        verbose_name='Галерея животного',
        related_name='%(class)s_related',
        related_query_name='%(class)s',
        blank=True
    )
    breed = models.CharField('Порода животного', max_length=100)
    admission_date = models.DateField(
        'Дата поступления в приют',
        default=date.today
    )
    shelter = models.ForeignKey(
        'Shelter',
        verbose_name='Приют',
        related_name='pets',
        on_delete=models.CASCADE
    )
    is_adopted = models.BooleanField('Нашел дом', default=False)

    class Meta:
        verbose_name = 'Питомец'
        verbose_name_plural = 'Питомцы'

    def __str__(self):
        return self.name


class Shelter(models.Model):
    """Карточка приюта."""
    is_approved = models.BooleanField('Приют проверен', default=False)
    owner = models.OneToOneField(
        User,
        verbose_name='Владелец приюта',
        related_name='shelter',
        on_delete=models.PROTECT
    )
    legal_owner_name = models.CharField('ФИО владельца приюта', max_length=50)
    tin = models.CharField(
        'ИНН',
        unique=True,
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$')]
    )
    name = models.CharField('Название приюта', unique=True, max_length=50)
    description = models.TextField('Описание приюта', max_length=1000)
    animal_types = models.ManyToManyField(
        'AnimalType',
        verbose_name='Виды животных',
        related_name='shelters'
    )
    logo = models.ImageField('Логотип приюта', null=True, blank=True)
    profile_image = models.ImageField('Фото профиля', null=True, blank=True)
    address = models.TextField('Адрес приюта', max_length=100, blank=True)
    long = models.DecimalField(
        'Долгота',
        max_digits=13,
        decimal_places=10,
        null=True,
        blank=True
    )
    lat = models.DecimalField(
        'Широта',
        max_digits=13,
        decimal_places=10,
        null=True,
        blank=True
    )
    phone_number = models.CharField(
        'Телефон приюта',
        max_length=12,
        validators=[RegexValidator(regex=r'^\+\d{11}$')]
    )
    working_from_hour = models.TimeField('Время начала работы')
    working_to_hour = models.TimeField('Время окончания работы')
    email = models.EmailField('Email приюта', unique=True, max_length=256)
    web_site = models.URLField('Сайт', max_length=200, blank=True)
    vk_page = models.URLField(
        'Группа в ВК',
        max_length=200,
        blank=True,
        validators=[RegexValidator(regex=r'^https://vk.com/')]
    )
    ok_page = models.URLField(
        'Группа в Одноклассниках',
        max_length=200,
        blank=True,
        validators=[RegexValidator(regex=r'^https://ok.ru/')]
    )
    telegram = models.URLField(
        'Телеграм канал',
        max_length=200,
        blank=True,
        validators=[RegexValidator(regex=r'^https://t.me/')]
    )

    objects = models.Manager()
    approved = ApprovedSheltersManager()

    class Meta:
        verbose_name = 'Приют'
        verbose_name_plural = 'Приюты'

    def save(self, *args, **kwargs):
        owner = self.owner
        owner.status = User.SHELTER_OWNER
        owner.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        owner = self.owner
        owner.status = User.USER
        owner.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name


class Task(models.Model):
    shelter = models.ForeignKey(
        'Shelter',
        verbose_name='Приют',
        related_name='tasks',
        on_delete=models.CASCADE
    )
    name = models.CharField('Краткое описание задачи', max_length=50)
    description = models.TextField('Описание задачи', max_length=500)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return self.name


class AnimalType(models.Model):
    slug = models.SlugField('Слаг', primary_key=True, max_length=20)
    name = models.CharField('Вид животного', unique=True, max_length=15)

    class Meta:
        verbose_name = 'Вид животного'
        verbose_name_plural = 'Виды животных'

    def __str__(self):
        return self.name
