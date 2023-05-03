from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from shelters.models import Shelter

User = get_user_model()


class Chat(models.Model):
    shelter = models.ForeignKey(
        Shelter,
        verbose_name='Приют',
        related_name='chats',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='chats',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'
        constraints = [
            models.UniqueConstraint(
                fields=['shelter', 'user'],
                name='unique_chat'
            )
        ]

    def clean(self):
        if self.shelter.owner.id == self.user.id:
            raise ValidationError('no_chat_with_own_shelter')

    def __str__(self):
        return f'{self.user} -> {self.shelter}'


class Message(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='messages',
        on_delete=models.CASCADE
    )
    chat = models.ForeignKey(
        Chat,
        verbose_name='Чат',
        related_name='messages',
        on_delete=models.CASCADE
    )
    text = models.TextField('Сообщение', max_length=200, blank=False)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    is_readed = models.BooleanField('Прочитано', default=False)
    is_edited = models.BooleanField('Изменено', default=False)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text[:20]
