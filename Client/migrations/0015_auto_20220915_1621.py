# Generated by Django 3.2.15 on 2022-09-15 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0014_vouchers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vouchers',
            name='product',
        ),
        migrations.RemoveField(
            model_name='vouchers',
            name='service',
        ),
        migrations.AddField(
            model_name='vouchers',
            name='voucher_type',
            field=models.CharField(choices=[('Product', 'Product'), ('Service', 'Service')], default='Product', max_length=20, verbose_name='Voucher Type'),
        ),
    ]
