# Generated by Django 4.0.6 on 2024-02-05 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0054_alter_salerecordappliedcoupons_coupon_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salerecordappliedcoupons',
            name='is_redeemed',
        ),
    ]