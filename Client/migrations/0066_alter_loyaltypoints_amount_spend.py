# Generated by Django 4.0.6 on 2023-06-05 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0065_loyaltypointlogs_checkout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loyaltypoints',
            name='amount_spend',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]