# Generated by Django 3.2.15 on 2022-11-21 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0017_auto_20221027_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentservice',
            name='price',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
