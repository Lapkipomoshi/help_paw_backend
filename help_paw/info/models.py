from django.db import models


class News(models.Model):
    header = models.CharField(
        'Заголовок', max_length=50,
        help_text='Введите заголовок новости, максимум 50 символов'
    )
    text = models.TextField(
        'Текст новости',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date', )

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

    def __str__(self):
        return self.about_us


class Vacancy(models.Model):
    shelter = models.ForeignKey(
        'shelters.Shelter',
        related_name='vacancy',
        on_delete=models.CASCADE,
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
