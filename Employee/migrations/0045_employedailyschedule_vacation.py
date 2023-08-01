# Generated by Django 4.0.6 on 2023-04-19 06:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0044_vacation_holiday_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='employedailyschedule',
            name='vacation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vacation_employedailyschedules', to='Employee.vacation'),
        ),
    ]
