# Generated by Django 3.2.15 on 2022-10-15 11:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Service', '0006_auto_20221015_1620'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='treatment_type',
            new_name='service_type',
        ),
    ]
