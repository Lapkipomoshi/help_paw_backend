# Generated by Django 4.1.4 on 2023-03-04 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shelters', '0011_animaltype_shelter_animal_types_and_more'),
        ('info', '0008_vacancy_delete_ownvacancy_delete_sheltervacancy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='shelter',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vacancy', to='shelters.shelter', verbose_name='Вакансия в приют'),
        ),
    ]
