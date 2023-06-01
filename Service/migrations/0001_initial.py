# Generated by Django 4.0.6 on 2022-08-24 06:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Business', '0009_businessvendor'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(default='', max_length=500)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_services', to='Business.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_services', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
