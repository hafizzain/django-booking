# Generated by Django 3.2.15 on 2023-02-09 05:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0042_productstock_order_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productstock',
            name='order_quantity',
        ),
    ]
