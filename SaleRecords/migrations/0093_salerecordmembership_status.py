# Generated by Django 4.0.6 on 2024-03-12 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0092_alter_salerecordmembership_is_installment'),
    ]

    operations = [
        migrations.AddField(
            model_name='salerecordmembership',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('In Active', 'In Active')], default='Active', max_length=50),
        ),
    ]