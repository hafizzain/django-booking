# Generated by Django 4.0.6 on 2022-09-05 11:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Business', '0015_auto_20220905_1059'),
        ('Service', '0001_initial'),
        ('Product', '0014_productmedia_is_cover'),
        ('Client', '0006_alter_clientgroup_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(default='', max_length=300)),
                ('days', models.PositiveIntegerField(default=0, verbose_name='Number of Days')),
                ('select_amount', models.CharField(choices=[('Limited', 'Limited'), ('Unlimited', 'Unlimited')], default='Limited', max_length=100)),
                ('services_count', models.PositiveIntegerField(default=0, verbose_name='Total Number of Services')),
                ('price', models.PositiveIntegerField(default=0, verbose_name='Subscription Price')),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_subscriptions', to='Business.business')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product_subscriptions', to='Product.product')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_subscriptions', to='Service.service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
