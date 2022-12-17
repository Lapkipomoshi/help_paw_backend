from django.db import models

from ..shelters.models import Shelter


class Vacancy(models.Model):
    shelter = models.ForeignKey(
        Shelter, related_name='vacancy', on_delete=models.CASCADE,
        verbose_name='Вакансия в приют'
    )
    position = models.CharField(
        'Доложность', max_length=30, help_text='Введите название должности'
    )
    description = models.TextField(
        'Описание', help_text='Опишите подробности вакансии'
    )
    pub_date = models.DateField('Дата публикации', auto_now_add=True)
    is_closed = models.BooleanField('Вакансия закрыта', default=False)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.position


class OwnVacancy(models.Model):
    position = models.CharField(
        'Доложность', max_length=30, help_text='Введите название должности'
    )
    description = models.TextField(
        'Описание', help_text='Опишите подробности вакансии'
    )
    pub_date = models.DateField('Дата публикации', auto_now_add=True)
    is_closed = models.BooleanField('Вакансия закрыта', default=False)

    class Meta:
        verbose_name = 'Своя Вакансия'
        verbose_name_plural = 'Свои Вакансии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.position


class Image(models.Model):
    image = models.ImageField(
        'Изображение', upload_to='temporary/',
        help_text='Выберите изображение для загрузки'
    )
    pub_date = models.DateTimeField('Дата загрузки', auto_now_add=True)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.image.name
