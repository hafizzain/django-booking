# Generated by Django 3.2.15 on 2022-12-17 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0032_auto_20221215_1311'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderstockproduct',
            name='status',
            field=models.CharField(choices=[('Placed', 'Placed'), ('Delivered', 'Delivered'), ('Partially_Received', 'Partially Received'), ('Received', 'Received'), ('Cancelled', 'Cancelled')], default='Placed', max_length=100),
        ),
    ]
