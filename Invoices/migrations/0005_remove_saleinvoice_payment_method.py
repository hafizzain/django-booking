# Generated by Django 4.0.6 on 2024-01-30 11:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Invoices', '0004_saleinvoice_payment_method'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saleinvoice',
            name='payment_method',
        ),
    ]