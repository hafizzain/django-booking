# Generated by Django 4.0.6 on 2023-12-25 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Promotions', '0015_rename_store_target_coupon_locations'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='type',
            field=models.TextField(null=True),
        ),
    ]
