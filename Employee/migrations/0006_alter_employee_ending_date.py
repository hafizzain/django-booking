# Generated by Django 4.0.6 on 2022-08-26 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0005_employee_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='ending_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
