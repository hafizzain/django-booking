# Generated by Django 4.0.6 on 2024-01-12 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HRM', '0008_holiday_employee_schedule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='holiday',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='holiday',
            name='start_date',
            field=models.DateField(),
        ),
    ]
