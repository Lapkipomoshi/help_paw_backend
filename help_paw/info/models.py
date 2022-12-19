from django.db import models


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
