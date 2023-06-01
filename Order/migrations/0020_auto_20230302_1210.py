# Generated by Django 3.2.18 on 2023-03-02 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0019_alter_order_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount_percentage',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='discount_price',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='price',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
