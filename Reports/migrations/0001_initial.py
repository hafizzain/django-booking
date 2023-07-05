# Generated by Django 4.0.6 on 2023-07-05 06:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Business', '0029_businessaddress_is_default'),
        ('Client', '0069_alter_loyaltypoints_number_points'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Invoices', '0004_saleinvoice_checkout'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountPromotionSalesReport',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('checkout_id', models.CharField(default='', max_length=900)),
                ('checkout_type', models.CharField(choices=[('Sale', 'Sale'), ('Appointment', 'Appointment')], default='Sale', max_length=20)),
                ('promotion_id', models.CharField(default='', max_length=900)),
                ('promotion_type', models.CharField(default='', max_length=900)),
                ('promotion_name', models.CharField(default='', max_length=900)),
                ('quantity', models.PositiveBigIntegerField(default=0)),
                ('gst', models.PositiveBigIntegerField(default=0)),
                ('total_price', models.DecimalField(decimal_places=5, default=0, max_digits=10)),
                ('discount_percentage', models.FloatField(default=0)),
                ('discount_price', models.FloatField(default=0)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client_discount_sales', to='Client.client')),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice_discount_sales', to='Invoices.saleinvoice')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_discount_sales', to='Business.businessaddress')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_discount_sales', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]