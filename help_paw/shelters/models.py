from django.db import models


class Shelter(models.Model):
    """Приют"""
    name_shelter = models.CharField(
        'Название приюта',
        max_length=100, 
        db_index=True
    )

    def __str__(self):
        return self.name_shelter


class Pet(models.Model):
    """Карточка животного"""
    name = models.CharField(
        'Кличка животного',
        max_length=100
    )
    category = models.ChoiceField(
        'Категория животного',
        max_length=100, 
        db_index=True
    )
    about_pet = models.TextField(
        'Описание животного',
        help_text='Расскажите о животном'
    )
    photo_pet = models.ImageField(
        'Фото животного',
        upload_to = 'photo/%Y/%m/%d/'
    )
    name_shelter = models.ForeignKey(Shelter,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return self.name