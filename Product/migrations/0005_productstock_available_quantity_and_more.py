# Generated by Django 4.0.6 on 2022-08-22 10:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0004_alter_product_vendor'),
    ]

    operations = [
        migrations.AddField(
            model_name='productstock',
            name='available_quantity',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='productstock',
            name='sold_quantity',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='productstock',
            name='quantity',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Total Quantity'),
        ),
    ]
