# Generated by Django 3.2.15 on 2022-12-28 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0037_auto_20221227_1315'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='full_price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='product_size',
        ),
        migrations.RemoveField(
            model_name='product',
            name='sell_price',
        ),
    ]
