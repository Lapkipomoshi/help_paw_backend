from django.db import models


class Pet(models.Model):
    """Карточка животного"""
    CAT = 'cat'
    DOG = 'dog'
    OTHER = 'other'

    ANIMAL_TYPE = [
        (CAT, 'Кошка'),
        (DOG, 'Собака'),
        (OTHER, 'Другое')
    ]
    name = models.CharField(
        'Кличка животного',
        max_length=100
    )
    animal_type = models.CharField(
        'Тип животного',
        choices=ANIMAL_TYPE,
        default=OTHER,
        max_length=10
    )
    about = models.TextField(
        'Описание животного',
        help_text='Расскажите о животном'
    )
    photo = models.ImageField(
        'Фото животного',
        upload_to='photo/%Y/%m/%d/'
    )
    shelter = models.ForeignKey(
        'Shelter',
        related_name='pets',
        on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = 'Питомец'
        verbose_name_plural = 'Питомцы'

    def __str__(self):
        return f'{self.name} - {self. animal_type}'


class Shelter(models.Model):
    name = models.CharField(
        'Название', max_length=30, unique=True,
        help_text='Введите название приюта'
    )
    description = models.TextField(
        'Описание приюта', help_text='Добавьте описание приюта'
    )
    logo = models.ImageField(
        'Логотип', null=True, blank=True, help_text='Загрузите логотип приюта'
    )
    address = models.TextField(
        'Адрес', null=True, blank=True, help_text='Укажите адрес приюта'
    )
    long = models.DecimalField('Долгота', max_digits=9, decimal_places=6)
    lat = models.DecimalField('Широта', max_digits=9, decimal_places=6)
    gallery = models.ManyToManyField(
        'info.Image', verbose_name='Галерея изображений'
    )

    class Meta:
        verbose_name = 'Приют'
        verbose_name_plural = 'Приюты'

    def __str__(self):
        return self.name


class Task(models.Model):
    shelter = models.ForeignKey(
        'Shelter', related_name='task', on_delete=models.CASCADE,
        verbose_name='Приют'
    )
    name = models.CharField(
        'Краткое описание', max_length=50,
        help_text='Напишите краткое описание задачи'
    )
    description = models.TextField(
        'Описание задачи', help_text='Опишите подробности задачи'
    )
    pub_date = models.DateField('Дата публикации', auto_now_add=True)
    is_emergency = models.BooleanField('Срочная задача', default=False)
    is_finished = models.BooleanField('Задача завершена', default=False)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.name
