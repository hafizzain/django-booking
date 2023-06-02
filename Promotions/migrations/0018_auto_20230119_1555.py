# Generated by Django 3.2.15 on 2023-01-19 10:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Service', '0024_priceservice_currency'),
        ('Business', '0028_businessaddress_description'),
        ('Promotions', '0017_auto_20230119_1113'),
    ]

    operations = [
        migrations.CreateModel(
            name='BundleFixed',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('spend_amount', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_bundlefixed', to='Business.business')),
                ('service', models.ManyToManyField(blank=True, null=True, related_name='service_bundlefixed', to='Service.Service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_bundlefixed', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='blockdate',
            name='bundlefixed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bundlefixed_blockdate', to='Promotions.bundlefixed'),
        ),
        migrations.AddField(
            model_name='daterestrictions',
            name='bundlefixed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bundlefixed_daterestrictions', to='Promotions.bundlefixed'),
        ),
        migrations.AddField(
            model_name='dayrestrictions',
            name='bundlefixed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bundlefixed_dayrestrictions', to='Promotions.bundlefixed'),
        ),
    ]
