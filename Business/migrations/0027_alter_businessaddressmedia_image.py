# Generated by Django 3.2.15 on 2022-12-21 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0026_alter_businessaddress_service_avaiable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessaddressmedia',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='business/address_media/'),
        ),
    ]
