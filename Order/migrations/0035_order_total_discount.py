# Generated by Django 4.0.6 on 2023-09-25 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0034_alter_order_discount_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_discount',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]
