# Generated by Django 4.1.4 on 2023-08-02 20:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelters', '0017_pet_animal_type_shelter_animal_types'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'verbose_name': 'Задача', 'verbose_name_plural': 'Задачи'},
        ),
        migrations.RemoveField(
            model_name='task',
            name='is_emergency',
        ),
        migrations.RemoveField(
            model_name='task',
            name='is_finished',
        ),
        migrations.RemoveField(
            model_name='task',
            name='pub_date',
        ),
        migrations.AlterField(
            model_name='task',
            name='shelter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='shelters.shelter', verbose_name='Приют'),
        ),
    ]
