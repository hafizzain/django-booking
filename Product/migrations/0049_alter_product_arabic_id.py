# Generated by Django 4.0.6 on 2023-07-12 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0048_product_arabic_id_product_arabic_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='arabic_id',
            field=models.CharField(default='', editable=False, max_length=999, unique=True),
        ),
    ]
