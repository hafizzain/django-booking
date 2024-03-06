# Generated by Django 4.0.6 on 2024-01-17 08:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Utility', '0001_initial_squashed_0018_state_unique_id'),
        ('Employee', '0035_giftdetail_currencies'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giftdetail',
            name='currencies',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gift_detail_currencies', to='Utility.currency'),
        ),
    ]