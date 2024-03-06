# Generated by Django 4.0.6 on 2024-02-13 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0067_alter_salerecords_checkout_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salerecords',
            name='status',
            field=models.CharField(choices=[('refund', 'Is Refund'), ('cancelled', 'Cancelled'), ('paid', 'Paid'), ('un_paid', 'Un Paid')], default='paid', max_length=50),
        ),
    ]