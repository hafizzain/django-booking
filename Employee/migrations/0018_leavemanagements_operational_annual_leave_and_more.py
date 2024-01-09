# Generated by Django 4.0.6 on 2024-01-09 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0017_giftcards'),
    ]

    operations = [
        migrations.AddField(
            model_name='leavemanagements',
            name='operational_annual_leave',
            field=models.IntegerField(default=0, help_text='Number of annual leaves allowed', null=True),
        ),
        migrations.AddField(
            model_name='leavemanagements',
            name='operational_casual_leave',
            field=models.IntegerField(default=0, help_text='Number of casual leaves allowed', null=True),
        ),
        migrations.AddField(
            model_name='leavemanagements',
            name='operational_leo_leave',
            field=models.IntegerField(default=0, help_text='Number of medical leaves allowed', null=True),
        ),
        migrations.AddField(
            model_name='leavemanagements',
            name='operational_medical_leave',
            field=models.IntegerField(default=0, help_text='Number of medical leaves allowed', null=True),
        ),
    ]
