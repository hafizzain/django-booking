# Generated by Django 3.2.18 on 2023-03-08 06:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0037_clientpackagevalidation'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientpackagevalidation',
            name='due_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='clientpackagevalidation',
            name='serviceduration',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='serviceduration_client_packagevalidation', to='Promotions.servicedurationforspecifictime'),
        ),
    ]
