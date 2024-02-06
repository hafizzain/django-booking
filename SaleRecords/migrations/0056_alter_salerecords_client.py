# Generated by Django 4.0.6 on 2024-02-06 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0008_alter_vouchers_end_date'),
        ('SaleRecords', '0055_remove_salerecordappliedcoupons_is_redeemed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salerecords',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale_records_client', to='Client.client'),
        ),
    ]
