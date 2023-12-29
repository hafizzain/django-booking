# Generated by Django 4.0.6 on 2023-12-29 06:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Finance', '0009_remove_refund_refunded_products_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='related_refund',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Finance.refund'),
            preserve_default=False,
        ),
    ]
