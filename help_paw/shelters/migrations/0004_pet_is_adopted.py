# Generated by Django 4.1.4 on 2023-01-29 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelters', '0003_shelter_is_approved_shelter_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='pet',
            name='is_adopted',
            field=models.BooleanField(default=False, verbose_name='Нашел дом'),
        ),
    ]
