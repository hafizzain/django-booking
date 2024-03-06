# Generated by Django 4.0.6 on 2023-12-22 12:45

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0001_initial_squashed_0074_client_is_image_uploaded_s3'),
        ('Service', '0001_initial_squashed_0032_alter_service_initial_deposit_alter_service_price'),
        ('Product', '0001_initial_squashed_0053_brand_is_image_uploaded_s3_and_more'),
        ('TragetControl', '0001_initial_squashed_0008_alter_retailtarget_brand_target_and_more'),
        ('Promotions', '0002_userrestricteddiscount_client'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('short_description', models.TextField(blank=True, null=True)),
                ('start_date', models.DateTimeField(null=True)),
                ('end_date', models.DateTimeField(null=True)),
                ('coupon_type', models.TextField(null=True)),
                ('block_day', models.TextField(null=True)),
                ('usage_limit', models.TextField(null=True)),
                ('user_limit', models.TextField(null=True)),
                ('code', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CouponDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupon_brand', to='Product.brand')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupon_client', to='Client.client')),
                ('coupon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupon', to='Promotions.coupon')),
                ('excluded_product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupon_excluded_product', to='Product.product')),
                ('service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupon_service', to='Service.service')),
                ('service_group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupon_service_group', to='Service.servicegroup')),
                ('store_target', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupon_storetarget', to='TragetControl.storetarget')),
            ],
        ),
    ]