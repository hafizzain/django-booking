# Generated by Django 4.0.6 on 2024-01-30 10:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0027_remove_salerecords_invoice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salerecords',
            name='refunds_data',
        ),
    ]