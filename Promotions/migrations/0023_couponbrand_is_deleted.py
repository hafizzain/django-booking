# Generated by Django 4.0.6 on 2023-12-25 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Promotions', '0022_coupon_buy_one_get_one_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponbrand',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]