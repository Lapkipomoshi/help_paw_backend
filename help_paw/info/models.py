from django.db import models

class News(models.Model):
    text = models.TextField(
        'Текст новости',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )


class Meta:
    ordering = ('-pub_date')

def __str__(self):
        return self.text