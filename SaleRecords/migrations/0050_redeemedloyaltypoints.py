# Generated by Django 4.0.6 on 2024-02-05 05:39

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0008_alter_vouchers_end_date'),
        ('SaleRecords', '0049_alter_purchasedgiftcards_sale_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='RedeemedLoyaltyPoints',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_blocked', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('redeemed_points', models.PositiveSmallIntegerField(blank=True, default=0, null=True)),
                ('clinet_loyalty_point', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='loyalty_points_records', to='Client.clientloyaltypoint')),
                ('sale_record', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applied_loyalty_points_records', to='SaleRecords.salerecords')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
