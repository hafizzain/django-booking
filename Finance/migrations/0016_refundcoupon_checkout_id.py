# Generated by Django 4.0.6 on 2024-02-28 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Finance', '0015_remove_refundcoupon_checkout_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='refundcoupon',
            name='checkout_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
