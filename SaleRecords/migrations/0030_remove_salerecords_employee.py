# Generated by Django 4.0.6 on 2024-01-30 13:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0029_salerecords_invoice_alter_salerecords_client'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salerecords',
            name='employee',
        ),
    ]
