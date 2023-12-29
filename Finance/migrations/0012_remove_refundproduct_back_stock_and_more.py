# Generated by Django 4.0.6 on 2023-12-29 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Finance', '0011_refundproduct_back_stock'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='refundproduct',
            name='back_stock',
        ),
        migrations.AddField(
            model_name='refundproduct',
            name='in_stock',
            field=models.BooleanField(default=True),
        ),
    ]
