# Generated by Django 4.0.6 on 2024-02-19 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0043_appointment_appointment_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='appointment_discount',
            field=models.FloatField(default=0),
        ),
    ]
