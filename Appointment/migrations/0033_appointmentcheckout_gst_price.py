# Generated by Django 3.2.18 on 2023-03-29 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0032_auto_20230302_1016'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentcheckout',
            name='gst_price',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
