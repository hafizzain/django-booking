# Generated by Django 4.0.6 on 2023-12-29 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0004_alter_employee_can_refunds'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='can_refund',
            field=models.BooleanField(default=True, null=True),
        ),
    ]
