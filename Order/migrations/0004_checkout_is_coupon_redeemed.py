# Generated by Django 4.0.6 on 2023-12-28 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0003_checkout_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='is_coupon_redeemed',
            field=models.TextField(null=True),
        ),
    ]
