# Generated by Django 4.0.6 on 2023-12-14 07:54

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0001_initial_squashed_0074_client_is_image_uploaded_s3'),
        ('Appointment', '0008_alter_opportunityemployeeservice_duration'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientMissedOpportunity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_blocked', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client_type', models.CharField(choices=[('IN HOUSE', 'IN HOUSE'), ('SALOON', 'SALOON')], max_length=200, null=True)),
                ('note', models.TextField()),
                ('date_time', models.DateTimeField()),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_missed_opportunities', to='Client.client')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='opportunityemployeeservice',
            name='client_missed_opportunity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='missed_opportunities', to='Client.client'),
        ),
        migrations.DeleteModel(
            name='MissedOpportunity',
        ),
    ]