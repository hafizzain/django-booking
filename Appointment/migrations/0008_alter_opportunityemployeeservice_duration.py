# Generated by Django 4.0.6 on 2023-12-14 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0007_remove_missedopportunity_employee_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opportunityemployeeservice',
            name='duration',
            field=models.CharField(default='', max_length=200),
        ),
    ]