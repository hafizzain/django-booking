# Generated by Django 3.2.15 on 2023-02-02 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0022_auto_20230201_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentservice',
            name='client_can_book',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='appointmentservice',
            name='slot_availible_for_online',
            field=models.CharField(default='', max_length=100),
        ),
    ]
