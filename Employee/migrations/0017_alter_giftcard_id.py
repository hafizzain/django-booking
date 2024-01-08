# Generated by Django 4.0.6 on 2024-01-08 07:23

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0016_giftcard'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giftcard',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
