# Generated by Django 4.0.6 on 2024-01-18 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0040_employedailyschedule_created_from_dashboard'),
    ]

    operations = [
        migrations.AddField(
            model_name='leavemanagements',
            name='used_annual',
            field=models.IntegerField(default=0, help_text='Number of casual leaves allowed', null=True),
        ),
        migrations.AddField(
            model_name='leavemanagements',
            name='used_casual',
            field=models.IntegerField(default=0, help_text='Number of casual leaves allowed', null=True),
        ),
        migrations.AddField(
            model_name='leavemanagements',
            name='used_medical',
            field=models.IntegerField(default=0, help_text='Number of casual leaves allowed', null=True),
        ),
    ]