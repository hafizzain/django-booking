# Generated by Django 4.0.6 on 2024-02-06 08:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0047_giftcards_is_custom_card'),
        ('Invoices', '0011_remove_saleinvoice_appointment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleinvoice',
            name='member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Employee.employee'),
        ),
    ]
