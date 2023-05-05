# Generated by Django 4.0.6 on 2023-05-05 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Promotions', '0030_productandgetspecific_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='bundlefixed',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
        migrations.AddField(
            model_name='complimentarydiscount',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
        migrations.AddField(
            model_name='directorflatdiscount',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
        migrations.AddField(
            model_name='fixedpriceservice',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
        migrations.AddField(
            model_name='mentionednumberservice',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
        migrations.AddField(
            model_name='packagesdiscount',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
        migrations.AddField(
            model_name='purchasediscount',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
        migrations.AddField(
            model_name='retailandgetservice',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
        migrations.AddField(
            model_name='specificbrand',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
        migrations.AddField(
            model_name='specificgroupdiscount',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
        migrations.AddField(
            model_name='spenddiscount',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
        migrations.AddField(
            model_name='spendsomeamount',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
        migrations.AddField(
            model_name='userrestricteddiscount',
            name='promotion_name',
            field=models.CharField(default='Promotion Name', max_length=999),
        ),
    ]
