# Generated by Django 3.2.18 on 2023-03-10 07:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0040_auto_20230310_1056'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membership',
            name='color',
        ),
    ]
