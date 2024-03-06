# Generated by Django 4.0.6 on 2024-01-24 11:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0002_client_client_tag_client_client_type'),
        ('Business', '0008_delete_refundsetting'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Appointment', '0030_reversal_url'),
        ('Finance', '0008_alter_refundcoupon_related_refund'),
        ('Product', '0003_productstock_refund_quantity'),
        ('Invoices', '0003_alter_saleinvoice_checkout_type'),
        ('Employee', '0042_employedailyschedule_last_state_of_schedule_and_more'),
        ('SaleRecords', '0002_remove_salerecords_coupon_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethods',
            name='amount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='redeemeditems',
            name='discount',
            field=models.FloatField(default=None),
        ),
        migrations.AlterField(
            model_name='redeemeditems',
            name='is_redeemed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='redeemeditems',
            name='redeem_option',
            field=models.CharField(default=None, max_length=250),
        ),
        migrations.AlterField(
            model_name='redeemeditems',
            name='redeemed_type',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='salerecordappliedcoupons',
            name='coupon_discounted_price',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='salerecords',
            name='business_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale_records_business_address', to='Business.businessaddress'),
        ),
        migrations.AlterField(
            model_name='salerecords',
            name='checkout_type',
            field=models.CharField(choices=[('appointment_checkout', 'Appointment Checkout'), ('sale_checkout', 'Sale Checkout')], default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='salerecords',
            name='client',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='sale_records_client', to='Client.client'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='salerecords',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Invoices.saleinvoice'),
        ),
        migrations.AlterField(
            model_name='salerecords',
            name='member',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='sale_records_member', to='Employee.employee'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='salerecords',
            name='refunds_data',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='refunds', to='Finance.refund'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='salerecords',
            name='sub_total',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='salerecords',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='sale_records_user', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='salerecordsappointmentservices',
            name='appointment',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='related_appointment', to='Appointment.appointment'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='salerecordsappointmentservices',
            name='reason',
            field=models.CharField(default=2, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='salerecordservices',
            name='price',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='salerecordsproducts',
            name='price',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='salerecordsproducts',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.product'),
        ),
        migrations.AlterField(
            model_name='salerecordsproducts',
            name='sale_record',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sale_products_records', to='SaleRecords.salerecords'),
        ),
        migrations.AlterField(
            model_name='salerecordtip',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_record_employee_tips', to='Employee.employee'),
        ),
        migrations.AlterField(
            model_name='salerecordtip',
            name='tip_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='saletax',
            name='business_tax_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Business.businesstax'),
        ),
    ]