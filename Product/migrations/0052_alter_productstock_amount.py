# Generated by Django 4.0.6 on 2023-08-03 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0051_alter_product_cost_price_alter_product_product_size_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productstock',
            name='amount',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Usage Amount'),
        ),
    ]