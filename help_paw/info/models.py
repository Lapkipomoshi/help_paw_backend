from django.db import models

from shelters.models import Shelter


class Article(models.Model):
    header = models.CharField(
        'Заголовок', max_length=50,
        help_text='Введите заголовок новости, максимум 50 символов'
    )
    text = models.TextField(
        'Текст новости', max_length=2000,
        help_text='Введите текст новости'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )
    profile_image = models.ImageField(
        'Основное изображение', help_text='Выберите основное изображение'
    )

    class Meta:
        abstract = True


class Vacancy(models.Model):
    position = models.CharField(
        'Доложность', max_length=30,
        help_text='Введите название должности'
    )
    description = models.TextField(
        'Описание', max_length=500,
        help_text='Опишите подробности вакансии'
    )
    pub_date = models.DateField('Дата публикации', auto_now_add=True)
    is_closed = models.BooleanField('Вакансия закрыта', default=False)

    class Meta:
        abstract = True


class News(Article):
    shelter = models.ForeignKey(
        Shelter, null=True, blank=True, default=None, on_delete=models.CASCADE,
        verbose_name='Новость от приюта', related_name='news'
    )
    image_1 = models.ImageField(
        'Фото 1', blank=True, help_text='Выберите дополнительное фото'
    )
    image_2 = models.ImageField(
        'Фото 2', blank=True, help_text='Выберите дополнительное фото'
    )
    image_3 = models.ImageField(
        'Фото 3', blank=True, help_text='Выберите дополнительное фото'
    )
    on_main = models.BooleanField('Отображать на главной', default=False)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.header[:10]


class HelpArticle(Article):
    source = models.URLField(
        'Источник', max_length=200,
        help_text='Укажите источник новости (url адрес)'
    )

    class Meta:
        verbose_name = 'Полезная статья'
        verbose_name_plural = 'Полезные статьи'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.header[:10]


class FAQ(models.Model):
    """Ответы на часто задаваемые вопросы"""

    question = models.CharField(
        'Заголовок вопроса',
        help_text='Вопрос для FAQ',
        max_length=200
    )
    answer = models.TextField(
        'Ответ на вопрос',
        help_text='Напишите четкий полезный ответ'
    )

    class Meta:
        ordering = ('question',)
        verbose_name_plural = 'Ответы на частые вопросы'

    def __str__(self):
        return self.question


class StaticInfo(models.Model):
    """Статическая информация на страничках"""

    about_us = models.TextField(
        'О компании',
        help_text='Расскажите о миссии, команде'
    )
    portfolio = models.TextField(
        'Портфолио',
        help_text='Разместите портфолио команды'
    )
    rewards = models.TextField(
        'Награды',
        help_text='Разместите информацию о наградах'
    )
    contacts = models.TextField(
        'Контакты',
        help_text='Укажите контакты'
    )

    class Meta:
        verbose_name_plural = 'Статичная информация'

    def __str__(self):
        return self.about_us


class ShelterVacancy(Vacancy):
    shelter = models.ForeignKey(
        Shelter, related_name='vacancy', on_delete=models.CASCADE,
        verbose_name='Вакансия в приют'
    )

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии приютов'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.position


class OwnVacancy(Vacancy):
    class Meta:
        verbose_name = 'Своя Вакансия'
        verbose_name_plural = 'Свои Вакансии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.position
