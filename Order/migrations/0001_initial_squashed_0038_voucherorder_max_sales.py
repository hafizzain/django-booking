# Generated by Django 4.0.6 on 2023-11-01 07:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    replaces = [('Order', '0001_initial'), ('Order', '0002_auto_20221022_1021'), ('Order', '0003_order_user'), ('Order', '0004_alter_order_payment_type'), ('Order', '0005_alter_order_status'), ('Order', '0006_auto_20221027_1503'), ('Order', '0007_order_sold_quantity'), ('Order', '0008_auto_20221107_1645'), ('Order', '0009_order_quantity'), ('Order', '0010_alter_checkout_client'), ('Order', '0011_alter_order_client'), ('Order', '0012_checkout_tip'), ('Order', '0013_auto_20230126_1737'), ('Order', '0014_auto_20230126_1739'), ('Order', '0015_auto_20230130_1533'), ('Order', '0016_auto_20230130_1606'), ('Order', '0017_auto_20230209_1639'), ('Order', '0018_alter_order_total_price'), ('Order', '0019_alter_order_total_price'), ('Order', '0020_auto_20230302_1210'), ('Order', '0021_checkout_is_promotion'), ('Order', '0022_alter_checkout_member'), ('Order', '0023_checkout_selected_promotion_id_and_more'), ('Order', '0024_redeemedmembership'), ('Order', '0025_alter_redeemedmembership_checkout_and_more'), ('Order', '0026_redeemmembershipitem_service_and_more'), ('Order', '0027_order_is_redeemed_order_redeemed_instance_id_and_more'), ('Order', '0028_checkout_tax_amount_checkout_tax_applied'), ('Order', '0029_alter_order_discount_price'), ('Order', '0030_alter_order_discount_percentage'), ('Order', '0031_alter_checkout_product_commission_and_more'), ('Order', '0032_checkout_tax_amount1_checkout_tax_applied1'), ('Order', '0033_checkout_tax_name_checkout_tax_name1'), ('Order', '0034_alter_order_discount_price'), ('Order', '0035_order_total_discount'), ('Order', '0036_checkout_total_discount_and_more'), ('Order', '0037_checkout_redeem_option_and_more'), ('Order', '0038_voucherorder_max_sales')]

    dependencies = [
        ('Employee', '0021_employee_location'),
        ('Client', '0032_auto_20221114_1155'),
        ('Service', '0015_alter_service_service_type'),
        ('Product', '0022_alter_product_product_size'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Employee', '0045_employedailyschedule_vacation'),
        ('Client', '0030_auto_20221102_1603'),
        ('Product', '0045_product_product_size'),
        ('Employee', '0020_auto_20221014_1252'),
        ('Service', '0024_priceservice_currency'),
        ('Client', '0055_vouchers_discount_percentage'),
        ('Business', '0022_business_is_completed'),
        ('Client', '0025_alter_subscription_select_amount'),
        ('Client', '0027_alter_vouchers_validity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('client_type', models.CharField(choices=[('Walk_in', 'Walk-in'), ('In_Saloon', 'In-Saloon')], default='', max_length=50)),
                ('payment_type', models.CharField(choices=[('Cash', 'Cash'), ('Voucher', 'Voucher'), ('SplitBill', 'SplitBill'), ('MasterCard', 'MasterCard'), ('Other', 'Other')], default='', max_length=50)),
                ('current_price', models.PositiveBigIntegerField(default=0)),
                ('tip', models.PositiveBigIntegerField(default=0)),
                ('gst', models.PositiveBigIntegerField(default=0)),
                ('total_price', models.PositiveBigIntegerField(default=0)),
                ('status', models.CharField(choices=[('Completed', 'Completed'), ('Incompleted', 'Incompleted'), ('Expired', 'Expired'), ('Active', 'Active')], default='Active', max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_orders', to='Client.client')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location_orders', to='Business.businessaddress')),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_orders', to='Employee.employee')),
                ('duration', models.CharField(choices=[('30_Min', '30 Min'), ('60_Min', '60 Min'), ('90_Min', '90 Min'), ('120_Min', '120 Min'), ('150_Min', '150 Min'), ('180_Min', '180 Min'), ('210_Min', '210 Min')], default='', max_length=50)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_sale_order', to=settings.AUTH_USER_MODEL)),
                ('promotion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_promotion_orders', to='Client.promotion')),
                ('rewards', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_reward_orders', to='Client.rewards')),
                ('sold_quantity', models.PositiveBigIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceOrder',
            fields=[
                ('order_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Order.order')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_orders', to='Service.service')),
            ],
            bases=('Order.order',),
        ),
        migrations.CreateModel(
            name='ProductOrder',
            fields=[
                ('order_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Order.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_orders', to='Product.product')),
            ],
            bases=('Order.order',),
        ),
        migrations.CreateModel(
            name='MemberShipOrder',
            fields=[
                ('order_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Order.order')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('membership', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership_orders', to='Client.membership')),
            ],
            bases=('Order.order',),
        ),
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('client_type', models.CharField(choices=[('Walk_in', 'Walk-in'), ('In_Saloon', 'In-Saloon')], default='', max_length=50)),
                ('payment_type', models.CharField(choices=[('Cash', 'Cash'), ('Voucher', 'Voucher'), ('SplitBill', 'SplitBill'), ('MasterCard', 'MasterCard'), ('Other', 'Other')], default='', max_length=50)),
                ('status', models.CharField(choices=[('Completed', 'Completed'), ('Incompleted', 'Incompleted'), ('Expired', 'Expired'), ('Active', 'Active')], default='Active', max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_checkout_orders', to='Client.client')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location_checkout_orders', to='Business.businessaddress')),
                ('member', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_checkout_orders', to='Employee.employee')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_checkout_order', to=settings.AUTH_USER_MODEL)),
                ('tip', models.FloatField(default=0)),
                ('product_commission', models.FloatField(blank=True, default=0, null=True)),
                ('service_commission', models.FloatField(blank=True, default=0, null=True)),
                ('voucher_commission', models.FloatField(blank=True, default=0, null=True)),
                ('product_commission_type', models.CharField(default='', max_length=50)),
                ('service_commission_type', models.CharField(default='', max_length=50)),
                ('voucher_commission_type', models.CharField(default='', max_length=50)),
                ('total_membership_price', models.FloatField(blank=True, default=0, null=True)),
                ('total_product_price', models.FloatField(blank=True, default=0, null=True)),
                ('total_service_price', models.FloatField(blank=True, default=0, null=True)),
                ('total_voucher_price', models.FloatField(blank=True, default=0, null=True)),
                ('is_promotion', models.BooleanField(default=False)),
                ('selected_promotion_id', models.CharField(default='', max_length=800)),
                ('selected_promotion_type', models.CharField(default='', max_length=400)),
                ('tax_amount', models.FloatField(default=0, verbose_name='Tax total amount')),
                ('tax_applied', models.FloatField(default=0, verbose_name='Tax Applied in Percentage')),
                ('tax_amount1', models.FloatField(default=0, verbose_name='Second Tax total amount')),
                ('tax_applied1', models.FloatField(default=0, verbose_name='Second Tax Applied in Percentage')),
                ('tax_name', models.CharField(default='', max_length=250)),
                ('tax_name1', models.CharField(default='', max_length=250)),
                ('total_discount', models.FloatField(blank=True, default=None, null=True)),
                ('redeem_option', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('voucher_redeem_percentage', models.FloatField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CheckoutPayment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('checkout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkout_paymentmethod', to='Order.checkout')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='checkout',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_orders', to='Order.checkout'),
        ),
        migrations.AddField(
            model_name='order',
            name='quantity',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_orders', to='Client.client'),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=5, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='discount_percentage',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='discount_price',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='price',
            field=models.FloatField(default=0),
        ),
        migrations.CreateModel(
            name='RedeemedMemberShip',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('checkout', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_redeemed_memberships', to='Order.checkout')),
                ('membership', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redeemed_memberships', to='Client.membership')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_redeemed_memberships', to='Order.order')),
            ],
        ),
        migrations.CreateModel(
            name='RedeemMembershipItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='redeemed_products', to='Product.product')),
                ('redeemed_membership', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redeem_items', to='Order.redeemedmembership')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='redeemed_services', to='Service.service')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='is_redeemed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='redeemed_instance_id',
            field=models.CharField(default='', max_length=800),
        ),
        migrations.AddField(
            model_name='order',
            name='redeemed_price',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='redeemed_type',
            field=models.CharField(default='', max_length=300),
        ),
        migrations.AlterField(
            model_name='order',
            name='current_price',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='gst',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='tip',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='total_discount',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.CreateModel(
            name='VoucherOrder',
            fields=[
                ('order_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Order.order')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('voucher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voucher_orders', to='Client.vouchers')),
                ('max_sales', models.IntegerField(default=0)),
            ],
            bases=('Order.order',),
        ),
    ]
