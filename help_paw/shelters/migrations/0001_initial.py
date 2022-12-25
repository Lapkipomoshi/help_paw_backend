# Generated by Django 4.1.4 on 2022-12-25 18:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('info', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shelter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название приюта', max_length=30, unique=True, verbose_name='Название')),
                ('description', models.TextField(help_text='Добавьте описание приюта', verbose_name='Описание приюта')),
                ('logo', models.ImageField(blank=True, help_text='Загрузите логотип приюта', null=True, upload_to='', verbose_name='Логотип')),
                ('address', models.TextField(blank=True, help_text='Укажите адрес приюта', null=True, verbose_name='Адрес')),
                ('long', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Долгота')),
                ('lat', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Широта')),
                ('gallery', models.ManyToManyField(to='info.image', verbose_name='Галерея изображений')),
            ],
            options={
                'verbose_name': 'Приют',
                'verbose_name_plural': 'Приюты',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Напишите краткое описание задачи', max_length=50, verbose_name='Краткое описание')),
                ('description', models.TextField(help_text='Опишите подробности задачи', verbose_name='Описание задачи')),
                ('pub_date', models.DateField(auto_now_add=True, verbose_name='Дата публикации')),
                ('is_emergency', models.BooleanField(default=False, verbose_name='Срочная задача')),
                ('is_finished', models.BooleanField(default=False, verbose_name='Задача завершена')),
                ('shelter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task', to='shelters.shelter', verbose_name='Приют')),
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Задачи',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Pet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Кличка животного')),
                ('animal_type', models.CharField(choices=[('cat', 'Кошка'), ('dog', 'Собака'), ('other', 'Другое')], default='other', max_length=10, verbose_name='Тип животного')),
                ('about', models.TextField(help_text='Расскажите о животном', verbose_name='Описание животного')),
                ('photo', models.ImageField(upload_to='photo/%Y/%m/%d/', verbose_name='Фото животного')),
                ('shelter', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pets', to='shelters.shelter')),
            ],
        ),
    ]
