# Generated by Django 4.0.6 on 2023-04-18 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0043_alter_employee_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacation',
            name='holiday_type',
            field=models.CharField(choices=[('Vacation', 'Vacation'), ('Absence', 'Absence')], default='Vacation', max_length=100),
        ),
    ]
