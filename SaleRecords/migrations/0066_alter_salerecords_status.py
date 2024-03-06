# Generated by Django 4.0.6 on 2024-02-09 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0065_alter_salerecords_checkout_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salerecords',
            name='status',
            field=models.CharField(choices=[('refund', 'Is Refund'), ('cancelled', 'Cancelled'), ('paid', 'Paid'), ('un_paid', 'Un Paid')], default='un_paid', max_length=50),
        ),
    ]