# Generated by Django 4.1.4 on 2023-01-29 16:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelters', '0004_pet_is_adopted'),
        ('info', '0004_alter_news_options_news_image_1_news_image_2_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(help_text='Введите заголовок новости, максимум 50 символов', max_length=50, verbose_name='Заголовок')),
                ('text', models.TextField(help_text='Введите текст поста', verbose_name='Текст новости')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('profile_image', models.ImageField(help_text='Выберите основное изображение', upload_to='', verbose_name='Основное изображение')),
                ('source', models.URLField(help_text='Укажите источник новости (url адрес)', verbose_name='Источник')),
            ],
            options={
                'verbose_name': 'Полезная статья',
                'verbose_name_plural': 'Полезные статьи',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.AddField(
            model_name='news',
            name='on_main',
            field=models.BooleanField(default=False, verbose_name='Отображать на главной'),
        ),
        migrations.AddField(
            model_name='news',
            name='shelter',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='news', to='shelters.shelter', verbose_name='Новость от приюта'),
        ),
    ]