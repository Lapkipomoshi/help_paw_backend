# Generated by Django 4.1.4 on 2023-03-04 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelters', '0011_animaltype_shelter_animal_types_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pet',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='sex',
            field=models.CharField(choices=[('male', 'самец'), ('female', 'самка'), ('other', 'другое')], default='other', max_length=6, verbose_name='Пол жиотного'),
        ),
    ]
