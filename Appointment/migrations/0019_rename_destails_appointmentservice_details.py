# Generated by Django 4.0.6 on 2022-12-02 12:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0018_appointmentservice_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointmentservice',
            old_name='destails',
            new_name='details',
        ),
    ]
