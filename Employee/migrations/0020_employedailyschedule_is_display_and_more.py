# Generated by Django 4.0.6 on 2024-01-10 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0019_employedailyschedule_is_holiday'),
    ]

    operations = [
        migrations.AddField(
            model_name='employedailyschedule',
            name='is_display',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employedailyschedule',
            name='vacation_status',
            field=models.TextField(null=True),
        ),
    ]