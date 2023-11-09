# Generated by Django 4.0.6 on 2023-11-01 07:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    replaces = [('Invoices', '0001_initial'), ('Invoices', '0002_alter_saleinvoice_business_address_and_more'), ('Invoices', '0003_alter_saleinvoice_appointment_service_and_more'), ('Invoices', '0004_saleinvoice_checkout'), ('Invoices', '0005_saleinvoice_file'), ('Invoices', '0006_saleinvoice_checkout_obj'), ('Invoices', '0007_remove_saleinvoice_checkout_obj')]

    dependencies = [
        ('Appointment', '0043_appointment_is_promotion_and_more'),
        ('Client', '0063_client_is_default'),
        # ('Business', '0029_businessaddress_is_default'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Order', '0034_alter_order_discount_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaleInvoice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('client_type', models.CharField(blank=True, choices=[('Walk_in', 'Walk-in'), ('In_Saloon', 'In-Saloon')], default='', max_length=50, null=True)),
                ('payment_type', models.CharField(blank=True, choices=[('Cash', 'Cash'), ('Voucher', 'Voucher'), ('SplitBill', 'SplitBill'), ('MasterCard', 'MasterCard'), ('Other', 'Other')], default='', max_length=50, null=True)),
                ('tip', models.FloatField(default=0)),
                ('total_service_price', models.FloatField(blank=True, default=0, null=True)),
                ('total_product_price', models.FloatField(blank=True, default=0, null=True)),
                ('total_voucher_price', models.FloatField(blank=True, default=0, null=True)),
                ('total_membership_price', models.FloatField(blank=True, default=0, null=True)),
                ('service_commission', models.FloatField(blank=True, default=0, null=True)),
                ('product_commission', models.FloatField(blank=True, default=0, null=True)),
                ('voucher_commission', models.FloatField(blank=True, default=0, null=True)),
                ('service_commission_type', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('product_commission_type', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('voucher_commission_type', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('is_promotion', models.BooleanField(default=False)),
                ('selected_promotion_id', models.CharField(blank=True, default='', max_length=800, null=True)),
                ('selected_promotion_type', models.CharField(blank=True, default='', max_length=400, null=True)),
                ('appointment_service', models.CharField(blank=True, default='', max_length=2000, null=True)),
                ('service', models.CharField(blank=True, default='', max_length=2000, null=True)),
                ('member', models.CharField(blank=True, default='', max_length=2000, null=True)),
                ('business_address', models.CharField(blank=True, default='', max_length=2000, null=True)),
                ('gst', models.FloatField(blank=True, default=0, null=True)),
                ('gst_price', models.FloatField(blank=True, default=0, null=True)),
                ('service_price', models.FloatField(blank=True, default=0, null=True)),
                ('total_price', models.FloatField(blank=True, default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Appointment.appointment')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Client.client')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Business.businessaddress')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('checkout', models.CharField(blank=True, max_length=128, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='invoicesFiles/')),
            ],
        ),
    ]
