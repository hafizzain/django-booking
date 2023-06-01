# Generated by Django 4.0.6 on 2023-05-16 05:46

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0055_vouchers_discount_percentage'),
        ('Order', '0023_checkout_selected_promotion_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RedeemedMemberShip',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('checkout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkout_redeemed_memberships', to='Order.checkout')),
                ('membership', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redeemed_memberships', to='Client.membership')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_redeemed_memberships', to='Order.order')),
            ],
        ),
    ]
