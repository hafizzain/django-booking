# Generated by Django 3.2.15 on 2022-09-27 08:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0012_auto_20220927_1003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workingdays',
            name='business',
        ),
    ]
