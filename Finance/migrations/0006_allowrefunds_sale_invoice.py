# Generated by Django 4.0.6 on 2024-01-09 13:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Invoices', '0001_initial_squashed_0007_remove_saleinvoice_checkout_obj'),
        ('Finance', '0005_allowrefunds_allowrefundpermissionsemployees'),
    ]

    operations = [
        migrations.AddField(
            model_name='allowrefunds',
            name='sale_invoice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Invoices.saleinvoice'),
        ),
    ]
