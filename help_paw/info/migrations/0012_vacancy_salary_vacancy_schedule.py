# Generated by Django 4.1.4 on 2023-03-04 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0011_alter_vacancy_description_alter_vacancy_position_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='salary',
            field=models.CharField(default=1, max_length=20, verbose_name='Оплата'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vacancy',
            name='schedule',
            field=models.CharField(default=1, max_length=30, verbose_name='Грфик работы'),
            preserve_default=False,
        ),
    ]
