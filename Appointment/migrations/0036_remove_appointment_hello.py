# Generated by Django 5.0.2 on 2024-02-10 05:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0035_appointment_hello'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='hello',
        ),
    ]
