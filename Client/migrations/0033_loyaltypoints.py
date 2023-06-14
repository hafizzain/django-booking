# Generated by Django 3.2.15 on 2022-12-08 05:25

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0032_auto_20221114_1155'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoyaltyPoints',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(default='', max_length=100)),
                ('loyaltytype', models.CharField(choices=[('Service', 'Service'), ('Retail', 'Retail'), ('Both', 'Both')], default='Service', max_length=50, verbose_name='Loyalty Type')),
                ('amount_spend', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('number_points', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('earn_points', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('total_earn_from_points', models.PositiveIntegerField(blank=True, default=0, null=True)),
            ],
        ),
    ]
