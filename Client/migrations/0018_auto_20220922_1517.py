# Generated by Django 3.2.15 on 2022-09-22 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0017_subscription_products_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotion',
            name='products',
        ),
        migrations.RemoveField(
            model_name='promotion',
            name='services',
        ),
        migrations.AddField(
            model_name='promotion',
            name='name',
            field=models.CharField(default='', max_length=100, verbose_name='Promotion Name'),
        ),
        migrations.AddField(
            model_name='promotion',
            name='purchases',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='No. of Purchases'),
        ),
    ]
