# Generated by Django 4.1.4 on 2024-03-06 17:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_user_donations_sum"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="donations_sum",
        ),
    ]