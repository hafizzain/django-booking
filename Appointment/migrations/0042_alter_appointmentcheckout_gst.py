# Generated by Django 4.0.6 on 2023-05-09 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0041_alter_appointmentcheckout_service_commission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointmentcheckout',
            name='gst',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
