# Generated by Django 4.0.6 on 2024-01-30 05:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0024_salerecordmembership_end_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salerecordvouchers',
            old_name='vouchers',
            new_name='voucher',
        ),
    ]