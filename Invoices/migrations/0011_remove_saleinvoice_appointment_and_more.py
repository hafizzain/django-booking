# Generated by Django 4.0.6 on 2024-02-06 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0047_giftcards_is_custom_card'),
        ('Invoices', '0010_remove_saleinvoice_gst_remove_saleinvoice_gst_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saleinvoice',
            name='appointment',
        ),
        migrations.RemoveField(
            model_name='saleinvoice',
            name='appointment_service',
        ),
        migrations.RemoveField(
            model_name='saleinvoice',
            name='business_address',
        ),
        migrations.RemoveField(
            model_name='saleinvoice',
            name='service',
        ),
        migrations.RemoveField(
            model_name='saleinvoice',
            name='tip',
        ),
        migrations.AlterField(
            model_name='saleinvoice',
            name='member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Employee.employee'),
        ),
    ]
