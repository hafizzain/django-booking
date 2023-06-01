# Generated by Django 3.2.15 on 2022-11-04 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0022_business_is_completed'),
        ('Product', '0023_productstock_product_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='location',
            field=models.ManyToManyField(related_name='location_product', to='Business.BusinessAddress'),
        ),
    ]
