# Generated by Django 4.0.6 on 2024-02-28 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0080_salerecordappliedcoupons_refund_coupon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salerecordappliedcoupons',
            name='refund_coupon',
        ),
    ]