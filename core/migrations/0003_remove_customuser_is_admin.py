# Generated by Django 5.1.2 on 2024-10-21 05:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_project_task'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_admin',
        ),
    ]