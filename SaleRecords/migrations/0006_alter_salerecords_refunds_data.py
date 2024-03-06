# Generated by Django 4.0.6 on 2024-01-24 12:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Finance', '0008_alter_refundcoupon_related_refund'),
        ('SaleRecords', '0005_rename_member_salerecords_employee_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salerecords',
            name='refunds_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='refunds', to='Finance.refund'),
        ),
    ]
