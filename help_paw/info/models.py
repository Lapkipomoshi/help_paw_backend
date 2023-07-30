from django.db import models

from shelters.models import Shelter


class Article(models.Model):
    header = models.CharField('Заголовок', max_length=50)
    text = models.TextField('Текст новости', max_length=2000)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    profile_image = models.ImageField('Основное изображение')
    gallery = models.ManyToManyField('gallery.Image',
                                     verbose_name='Галерея',
                                     related_name='%(class)s_related',
                                     related_query_name='%(class)s',
                                     blank=True)

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
    on_main = models.BooleanField('Отображать на главной', default=False)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ('-pub_date',)

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
    salary = models.PositiveIntegerField('Оплата')
    is_ndfl = models.BooleanField('НДФЛ', default=False)
    education = models.ForeignKey(
        'Education',
        verbose_name='Образование',
        related_name='vacancies',
        on_delete=models.PROTECT
    )
    schedule = models.ManyToManyField(
        'Schedule',
        verbose_name='График работы',
        related_name='vacancies'
    )
    position = models.CharField('Доложность', max_length=30)
    description = models.TextField('Описание', max_length=500)
    pub_date = models.DateField('Дата публикации', auto_now_add=True)
    is_closed = models.BooleanField('Вакансия закрыта', default=False)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.position


class Schedule(models.Model):
    slug = models.SlugField(primary_key=True, max_length=25)
    names = models.CharField(max_length=25)

    class Meta:
        verbose_name = 'График работы'
        verbose_name_plural = 'Графики работы'

    def __str__(self):
        return self.names


class Education(models.Model):
    slug = models.SlugField(primary_key=True, max_length=25)
    name = models.CharField(max_length=25)

    class Meta:
        verbose_name = 'Образование'
        verbose_name_plural = 'Образование'

    def __str__(self):
        return self.name
