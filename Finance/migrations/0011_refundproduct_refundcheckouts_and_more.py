# Generated by Django 4.0.6 on 2024-02-13 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Finance', '0010_refundservices_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='refundproduct',
            name='refundcheckouts',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='refundservices',
            name='refundcheckouts',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
