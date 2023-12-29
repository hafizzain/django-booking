# Generated by Django 4.0.6 on 2023-12-29 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reports', '0004_alter_couponreport_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponreport',
            name='amount_spent',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='couponreport',
            name='client_type',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='couponreport',
            name='coupon_type_value',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='couponreport',
            name='discounted_percentage',
            field=models.FloatField(null=True),
        ),
    ]
