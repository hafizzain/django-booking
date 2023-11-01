# Generated by Django 3.2.15 on 2022-12-08 05:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Client', '0033_loyaltypoints'),
    ]

    operations = [
        migrations.AddField(
            model_name='loyaltypoints',
            name='business',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_loyalty', to='Business.business'),
        ),
        migrations.AddField(
            model_name='loyaltypoints',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='loyaltypoints',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='loyaltypoints',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='loyaltypoints',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='loyaltypoints',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_loyalty', to=settings.AUTH_USER_MODEL, verbose_name='Creator ( User )'),
        ),
    ]
