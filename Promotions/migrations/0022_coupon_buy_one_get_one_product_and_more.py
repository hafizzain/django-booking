# Generated by Django 4.0.6 on 2023-12-25 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Service', '0001_initial_squashed_0032_alter_service_initial_deposit_alter_service_price'),
        ('Product', '0001_initial_squashed_0053_brand_is_image_uploaded_s3_and_more'),
        ('Promotions', '0021_coupon_buy_one_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='buy_one_get_one_product',
            field=models.ManyToManyField(null=True, related_name='buy_one_get_one_product', to='Product.product'),
        ),
        migrations.AddField(
            model_name='coupon',
            name='buy_one_get_one_service',
            field=models.ManyToManyField(null=True, related_name='buy_one_get_one_service', to='Service.service'),
        ),
    ]
