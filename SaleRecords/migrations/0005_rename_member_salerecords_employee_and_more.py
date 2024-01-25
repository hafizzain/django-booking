# Generated by Django 4.0.6 on 2024-01-24 12:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Client', '0002_client_client_tag_client_client_type'),
        ('SaleRecords', '0004_alter_salerecords_business_address_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salerecords',
            old_name='member',
            new_name='employee',
        ),
        migrations.AlterField(
            model_name='salerecords',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sale_records_client', to='Client.client'),
        ),
        migrations.AlterField(
            model_name='salerecords',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sale_records_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
