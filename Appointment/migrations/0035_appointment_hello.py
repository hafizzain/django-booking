# Generated by Django 5.0.2 on 2024-02-10 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0034_appointmentgroup_group_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='hello',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
    ]
