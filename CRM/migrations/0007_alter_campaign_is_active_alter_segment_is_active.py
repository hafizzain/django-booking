# Generated by Django 4.0.6 on 2023-12-28 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0006_alter_campaign_is_active_alter_segment_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='segment',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
