# Generated by Django 4.0.6 on 2023-12-23 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Promotions', '0005_rename_client_coupon_clients_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='coupon_type_value',
            field=models.TextField(null=True),
        ),
    ]
