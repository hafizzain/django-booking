# Generated by Django 4.0.6 on 2024-02-06 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0008_delete_refundsetting'),
        ('Product', '0003_productstock_refund_quantity'),
        ('Service', '0003_servicegroup_image_servicegroup_is_image_uploaded_s3'),
        ('Deal', '0005_dealdate_deal_terms_dealrestriction_dealmedia_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dealrestriction',
            name='block_dates',
            field=models.ManyToManyField(blank=True, to='Deal.dealdate'),
        ),
        migrations.AlterField(
            model_name='dealrestriction',
            name='excluded_locations',
            field=models.ManyToManyField(blank=True, to='Business.businessaddress'),
        ),
        migrations.AlterField(
            model_name='dealrestriction',
            name='excluded_products',
            field=models.ManyToManyField(blank=True, to='Product.product'),
        ),
        migrations.AlterField(
            model_name='dealrestriction',
            name='excluded_services',
            field=models.ManyToManyField(blank=True, to='Service.service'),
        ),
    ]
