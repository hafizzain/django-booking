# Generated by Django 3.2.15 on 2022-11-01 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0022_business_is_completed'),
        ('Employee', '0020_auto_20221014_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='location',
            field=models.ManyToManyField(related_name='location_employee', to='Business.BusinessAddress'),
        ),
    ]
