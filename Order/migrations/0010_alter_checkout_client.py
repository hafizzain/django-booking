# Generated by Django 3.2.15 on 2022-11-15 11:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0032_auto_20221114_1155'),
        ('Order', '0009_order_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkout',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_checkout_orders', to='Client.client'),
        ),
    ]
