# Generated by Django 3.2.15 on 2022-12-09 06:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0022_business_is_completed'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Employee', '0027_vacation'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacation',
            name='business',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_vacation', to='Business.business'),
        ),
        migrations.AddField(
            model_name='vacation',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_vacation', to=settings.AUTH_USER_MODEL),
        ),
    ]
