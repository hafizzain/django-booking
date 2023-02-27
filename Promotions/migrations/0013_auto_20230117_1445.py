# Generated by Django 3.2.15 on 2023-01-17 09:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Service', '0024_priceservice_currency'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Business', '0028_businessaddress_description'),
        ('Promotions', '0012_auto_20230117_0948'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spendsomeamount',
            name='service',
        ),
        migrations.RemoveField(
            model_name='spendsomeamount',
            name='spend_amount',
        ),
        migrations.CreateModel(
            name='SpendSomeAmountAndGetDiscount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('spend_amount', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_spendandgetdiscount', to='Business.business')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_spendandgetdiscount', to='Service.service')),
                ('spandsomeamount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='spendandgetdiscount_spendsomeamount', to='Promotions.spendsomeamount')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_spendandgetdiscount', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
