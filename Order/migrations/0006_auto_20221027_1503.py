# Generated by Django 3.2.15 on 2022-10-27 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0027_alter_vouchers_validity'),
        ('Order', '0005_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='promotion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_promotion_orders', to='Client.promotion'),
        ),
        migrations.AddField(
            model_name='order',
            name='rewards',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_reward_orders', to='Client.rewards'),
        ),
    ]
