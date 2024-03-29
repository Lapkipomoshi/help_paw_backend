# Generated by Django 4.1.4 on 2023-02-06 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.CharField(choices=[('shelter_owner', 'Владелец приюта'), ('user', 'Пользователь'), ('admin', 'Администратор'), ('moderator', 'Модератор контента')], default='user', help_text='Выберите статус пользователя', max_length=50, verbose_name='Статус'),
        ),
    ]
