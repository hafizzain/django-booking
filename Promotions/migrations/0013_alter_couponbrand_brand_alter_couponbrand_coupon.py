# Generated by Django 4.0.6 on 2023-12-25 07:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0001_initial_squashed_0053_brand_is_image_uploaded_s3_and_more'),
        ('Promotions', '0012_alter_couponbrand_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponbrand',
            name='brand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aval_coupon_brand', to='Product.brand'),
        ),
        migrations.AlterField(
            model_name='couponbrand',
            name='coupon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aval_coupon_brands', to='Promotions.coupon'),
        ),
    ]
