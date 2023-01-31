# Generated by Django 4.1.4 on 2023-01-29 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shelters', '0004_pet_is_adopted'),
        ('info', '0002_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Vacancy',
            new_name='ShelterVacancy',
        ),
        migrations.DeleteModel(
            name='Image',
        ),
        migrations.AlterModelOptions(
            name='sheltervacancy',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Вакансия', 'verbose_name_plural': 'Вакансии приютов'},
        ),
    ]