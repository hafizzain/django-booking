# Generated by Django 4.0.6 on 2023-10-12 07:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MultiLanguage', '0006_translationlabels'),
        ('Business', '0035_businessaddress_secondary_translation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessaddress',
            name='primary_translation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary', to='MultiLanguage.invoicetranslation'),
        ),
        migrations.AlterField(
            model_name='businessaddress',
            name='secondary_translation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='secondary', to='MultiLanguage.invoicetranslation'),
        ),
    ]