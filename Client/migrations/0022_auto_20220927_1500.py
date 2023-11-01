# Generated by Django 3.2.15 on 2022-09-27 10:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0021_auto_20220926_1508'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membership',
            name='color',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='description',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='session',
        ),
        migrations.AddField(
            model_name='membership',
            name='membership',
            field=models.CharField(choices=[('Product', 'Product'), ('Service', 'Service')], default='Product', max_length=30),
        ),
        migrations.AddField(
            model_name='membership',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product_memberships', to='Product.product'),
        ),
        migrations.AddField(
            model_name='membership',
            name='total_number',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
