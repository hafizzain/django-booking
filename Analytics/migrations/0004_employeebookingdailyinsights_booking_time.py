# Generated by Django 4.0.6 on 2023-08-28 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Analytics', '0003_alter_employeebookingdailyinsights_day_time_choice'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeebookingdailyinsights',
            name='booking_time',
            field=models.TimeField(blank=True, null=True, verbose_name='Appointment Start Time'),
        ),
    ]
