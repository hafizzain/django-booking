# Generated by Django 3.2.15 on 2022-09-02 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0012_alter_product_barcode_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='tax_rate',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='productstock',
            name='amount',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Usage Amount'),
        ),
        migrations.AlterField(
            model_name='productstock',
            name='unit',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Usage Unit'),
        ),
    ]
