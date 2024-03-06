# Generated by Django 4.0.6 on 2024-01-25 11:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0002_client_client_tag_client_client_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='avaliableclient/images/')),
                ('is_image_uploaded_s3', models.BooleanField(default=False)),
                ('file_name', models.TextField(blank=True, null=True)),
                ('file_type', models.TextField(blank=True, null=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Client.client')),
            ],
        ),
    ]
