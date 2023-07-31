# Generated by Django 4.0.6 on 2023-07-26 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MultiLanguage', '0005_invoicetranslation_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranslationLabels',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.TextField(blank=True, null=True)),
                ('value', models.TextField(blank=True, null=True)),
                ('english_name', models.TextField(blank=True, null=True)),
                ('order', models.IntegerField(blank=True, null=True)),
                ('language', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='MultiLanguage.language')),
            ],
            options={
                'ordering': ['-order'],
            },
        ),
    ]
