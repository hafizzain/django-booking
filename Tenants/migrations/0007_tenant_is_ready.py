# Generated by Django 4.0.6 on 2023-02-21 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tenants', '0006_employeetenantdetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='is_ready',
            field=models.BooleanField(default=False),
        ),
    ]
