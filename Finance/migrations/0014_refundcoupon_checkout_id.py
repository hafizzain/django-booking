# Generated by Django 4.0.6 on 2024-02-28 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Finance', '0013_alter_refund_refund_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='refundcoupon',
            name='checkout_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
