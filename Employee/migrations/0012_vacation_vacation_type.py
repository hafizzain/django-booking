# Generated by Django 4.0.6 on 2024-01-02 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0011_employedailyschedule_is_leo_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacation',
            name='vacation_type',
            field=models.TextField(null=True),
        ),
    ]
