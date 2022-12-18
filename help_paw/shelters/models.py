from django.db import models




class Pet(models.Model):
    """Карточка животного"""
    
    ANIMAL_TYPE = [
    ('DOG', 'dog'),
    ('CAT', 'cat'),
]
    name = models.CharField(
        'Кличка животного',
        max_length=100
    )
    animal_type = models.ChoiceField(
        'Тип животного',
        choices=ANIMAL_TYPE,
        default = None,
        max_length = 10     
    )
    about = models.TextField(
        'Описание животного',
        help_text='Расскажите о животном'
    )
    photo = models.ImageField(
        'Фото животного',
        upload_to = 'photo/%Y/%m/%d/'
    )
    shelter = models.ForeignKey(
        'Shelter',
        related_name='pets',
        on_delete=models.PROTECT
    )

    def __str__(self):
        return self.name
