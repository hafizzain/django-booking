# Generated by Django 4.0.6 on 2023-12-25 02:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Promotions', '0013_alter_coupon_amount_spent_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='brands',
        ),
    ]
