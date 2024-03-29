# Generated by Django 4.0.6 on 2023-12-28 06:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Promotions', '0027_alter_coupon_usage_limit_alter_coupon_user_limit'),
        ('Order', '0002_checkout_coupon_discounted_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='coupon',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupon_checkout', to='Promotions.coupon'),
        ),
    ]
