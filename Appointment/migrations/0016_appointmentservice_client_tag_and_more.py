# Generated by Django 4.0.6 on 2023-12-26 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0015_appointmentcheckout_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentservice',
            name='client_tag',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='appointmentservice',
            name='client_type',
            field=models.CharField(default='', max_length=50),
        ),
    ]