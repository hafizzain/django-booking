# Generated by Django 3.2.15 on 2022-11-07 06:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Client', '0030_auto_20221102_1603'),
        ('Business', '0001_initial_squashed_0038_alter_businessvendor_email'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(default='', max_length=300)),
                ('segemnt_type', models.CharField(choices=[('Static', 'Static'), ('Dynamic', 'Dynamic')], default='Dynamic', max_length=30, verbose_name='Segment Type')),
                ('description', models.CharField(blank=True, max_length=300, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_segment', to='Business.business')),
                ('client', models.ManyToManyField(related_name='segment_clients', to='Client.Client')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='segment', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
