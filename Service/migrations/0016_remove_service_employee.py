# Generated by Django 3.2.15 on 2022-10-24 05:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Service', '0015_alter_service_service_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='employee',
        ),
    ]
