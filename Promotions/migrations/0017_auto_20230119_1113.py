# Generated by Django 3.2.15 on 2023-01-19 06:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Service', '0024_priceservice_currency'),
        ('Business', '0028_businessaddress_description'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Promotions', '0016_auto_20230118_1251'),
    ]

    operations = [
        migrations.CreateModel(
            name='MentionedNumberService',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_mentionednumberservice', to='Business.business')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_mentionednumberservice', to='Service.service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_mentionednumberservice', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FreeService',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('quantity', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('mentionnumberservice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='freeservice_mentionnumberservice', to='Promotions.mentionednumberservice')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_freeservice', to='Service.service')),
            ],
        ),
        migrations.AddField(
            model_name='blockdate',
            name='mentionednumberservice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mentionednumberservice_blockdate', to='Promotions.mentionednumberservice'),
        ),
        migrations.AddField(
            model_name='daterestrictions',
            name='mentionednumberservice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mentionednumberservice_daterestrictions', to='Promotions.mentionednumberservice'),
        ),
        migrations.AddField(
            model_name='dayrestrictions',
            name='mentionednumberservice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mentionednumberservice_dayrestrictions', to='Promotions.mentionednumberservice'),
        ),
    ]
