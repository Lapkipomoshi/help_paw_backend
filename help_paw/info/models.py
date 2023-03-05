from django.db import models

from shelters.models import Shelter


class Article(models.Model):
    header = models.CharField('Заголовок', max_length=50)
    text = models.TextField('Текст новости', max_length=2000)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    profile_image = models.ImageField('Основное изображение')

    class Meta:
        abstract = True


class News(Article):
    shelter = models.ForeignKey(
        Shelter,
        verbose_name='Новость от приюта',
        related_name='news',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    image_1 = models.ImageField('Фото 1', blank=True)
    image_2 = models.ImageField('Фото 2', blank=True)
    image_3 = models.ImageField('Фото 3', blank=True)
    on_main = models.BooleanField('Отображать на главной', default=False)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.header[:10]


class HelpArticle(Article):
    source = models.URLField('url адрес источника', max_length=200)

    class Meta:
        verbose_name = 'Полезная статья'
        verbose_name_plural = 'Полезные статьи'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.header[:10]


class FAQ(models.Model):
    """Ответы на часто задаваемые вопросы."""
    question = models.CharField('Вопрос', max_length=200)
    answer = models.TextField('Ответ', max_length=500)

    class Meta:
        ordering = ('question',)
        verbose_name_plural = 'Ответы на частые вопросы'

    def __str__(self):
        return self.question


class StaticInfo(models.Model):
    """Статическая информация на страничках."""
    about_us = models.TextField('О компании')
    portfolio = models.TextField('Портфолио')
    rewards = models.TextField('Награды')
    contacts = models.TextField('Контакты')

    class Meta:
        verbose_name_plural = 'Статичная информация'

    def __str__(self):
        return self.about_us


class Vacancy(models.Model):
    shelter = models.ForeignKey(
        Shelter,
        verbose_name='Вакансия в приюте',
        related_name='vacancy',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    salary = models.CharField('Оплата', max_length=20)
    schedule = models.CharField('Грфик работы', max_length=30)
    position = models.CharField('Доложность', max_length=30)
    description = models.TextField('Описание', max_length=500)
    pub_date = models.DateField('Дата публикации', auto_now_add=True)
    is_closed = models.BooleanField('Вакансия закрыта', default=False)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.position
