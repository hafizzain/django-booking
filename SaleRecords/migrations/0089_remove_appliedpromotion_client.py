# Generated by Django 4.0.6 on 2024-03-08 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0088_appliedpromotion_client'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appliedpromotion',
            name='client',
        ),
    ]