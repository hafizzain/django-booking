# Generated by Django 3.2.15 on 2022-12-20 06:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Business', '0023_businessaddress_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessaddress',
            name='location_name',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AddField(
            model_name='businessaddress',
            name='service_avaiable',
            field=models.CharField(choices=[('Everyone', 'Everyone'), ('Busines', 'Busines')], default='Busines', max_length=100),
        ),
        migrations.CreateModel(
            name='BusinessAddressMedia',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='business/addres_media/')),
                ('is_cover', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_businessaddress_media', to='Business.business')),
                ('business_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_address_businessaddress_media', to='Business.businessaddress')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_businessaddress_media', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
