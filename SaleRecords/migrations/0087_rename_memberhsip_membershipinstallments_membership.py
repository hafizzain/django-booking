# Generated by Django 4.0.6 on 2024-03-08 05:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0086_alter_redeemedloyaltypoints_redeemed_points'),
    ]

    operations = [
        migrations.RenameField(
            model_name='membershipinstallments',
            old_name='memberhsip',
            new_name='membership',
        ),
    ]