# Generated by Django 4.0.6 on 2023-11-01 07:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    replaces = [('Promotions', '0001_initial'), ('Promotions', '0002_auto_20230109_1638'), ('Promotions', '0003_auto_20230110_1452'), ('Promotions', '0004_purchasediscount_servicegroupdiscount_specificgroupdiscount'), ('Promotions', '0005_auto_20230111_1141'), ('Promotions', '0006_alter_dayrestrictions_directorflat'), ('Promotions', '0007_auto_20230112_1136'), ('Promotions', '0008_auto_20230112_1200'), ('Promotions', '0009_spenddiscount'), ('Promotions', '0010_auto_20230113_2356'), ('Promotions', '0011_auto_20230116_2339'), ('Promotions', '0012_auto_20230117_0948'), ('Promotions', '0013_auto_20230117_1445'), ('Promotions', '0014_auto_20230117_1516'), ('Promotions', '0015_fixedpriceservice'), ('Promotions', '0016_auto_20230118_1251'), ('Promotions', '0017_auto_20230119_1113'), ('Promotions', '0018_auto_20230119_1555'), ('Promotions', '0019_productandgetspecific_retailandgetservice'), ('Promotions', '0020_auto_20230120_1641'), ('Promotions', '0021_userrestricteddiscount'), ('Promotions', '0022_auto_20230121_1124'), ('Promotions', '0023_auto_20230121_1130'), ('Promotions', '0024_complimentarydiscount_discountonfreeservice'), ('Promotions', '0025_auto_20230123_1132'), ('Promotions', '0026_auto_20230125_1042'), ('Promotions', '0027_auto_20230125_1328'), ('Promotions', '0028_servicegroupdiscount_brand_and_more'), ('Promotions', '0029_productandgetspecific_promotion_type'), ('Promotions', '0030_productandgetspecific_brand'), ('Promotions', '0031_bundlefixed_promotion_name_and_more'), ('Promotions', '0032_promotionexcludeditem'), ('Promotions', '0033_alter_bundlefixed_spend_amount_and_more')]

    dependencies = [
        ('Product', '0045_product_product_size'),
        # ('Client', '0035_alter_client_user'),
        ('Service', '0024_priceservice_currency'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Product', '0041_productorderstockreport_reorder_quantity'),
        # ('Business', '0028_businessaddress_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectOrFlatDiscount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_directorflatdiscount', to='Business.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_directorflatdiscount', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='SpecificGroupDiscount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='businessgroup_specific_discount', to='Business.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_specificgroup_discount', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseDiscount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('select_type', models.CharField(choices=[('Service', 'Service'), ('Product', 'Product')], default='Product', max_length=50)),
                ('purchase', models.FloatField(blank=True, default=0, null=True)),
                ('discount_value', models.FloatField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_purchase_discount', to='Business.business')),
                ('discount_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discountproduct_purchase_discount', to='Product.product')),
                ('discount_service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discountservice_purchase_discount', to='Service.service')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_purchase_discount', to='Product.product')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_purchase_discount', to='Service.service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_purchase_discount', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='SpendDiscount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('spend_amount', models.FloatField(blank=True, default=0, null=True)),
                ('select_type', models.CharField(choices=[('Service', 'Service'), ('Product', 'Product')], default='Service', max_length=50)),
                ('discount_value', models.FloatField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_spend_discount', to='Business.business')),
                ('discount_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discountproduct_spend_discount', to='Product.product')),
                ('discount_service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discountservice_spend_discount', to='Service.service')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_spend_discount', to='Service.service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_spend_discount', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='SpecificBrand',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('discount_brand', models.FloatField(blank=True, default=0, null=True)),
                ('discount_service_group', models.FloatField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='brand_specific_brand', to='Product.brand')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_specific_brand', to='Business.business')),
                ('servicegroup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicegroup_specific_brand', to='Service.servicegroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_specific_brand', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='SpendSomeAmount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_spendsomeamount', to='Business.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_spendsomeamount', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='FixedPriceService',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('spend_amount', models.FloatField(blank=True, default=0, null=True)),
                ('duration', models.CharField(default='', max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_fixedpriceservice', to='Business.business')),
                ('service', models.ManyToManyField(blank=True, null=True, related_name='service_fixedpriceservice', to='Service.service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_fixedpriceservice', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='MentionedNumberService',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_mentionednumberservice', to='Business.business')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_mentionednumberservice', to='Service.service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_mentionednumberservice', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='FreeService',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('quantity', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('mentionnumberservice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='freeservice_mentionnumberservice', to='Promotions.mentionednumberservice')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_freeservice', to='Service.service')),
            ],
        ),
        migrations.CreateModel(
            name='BundleFixed',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('spend_amount', models.FloatField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_bundlefixed', to='Business.business')),
                ('service', models.ManyToManyField(blank=True, null=True, related_name='service_bundlefixed', to='Service.service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_bundlefixed', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='RetailAndGetService',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_retailandgetservice', to='Business.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_retailandgetservice', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='UserRestrictedDiscount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('corporate_type', models.CharField(choices=[('All_Service', 'All Service'), ('Retail_Product', 'Retail Product')], default='All_Service', max_length=50)),
                ('discount_percentage', models.FloatField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_userrestricteddiscount', to='Business.business')),
                # ('client', models.ManyToManyField(related_name='client_userrestricteddiscount', to='Client.client')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_userrestricteddiscount', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='ComplimentaryDiscount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_complimentrydiscount', to='Business.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_complimentrydiscount', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='PackagesDiscount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_packagesdiscount', to='Business.business')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_packagesdiscount', to=settings.AUTH_USER_MODEL)),
                ('promotion_name', models.CharField(default='Promotion Name', max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='BlockDate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date', models.DateField(null=True, verbose_name='Block Date')),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('directorflat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='directorflat_blockdate', to='Promotions.directorflatdiscount')),
                ('specificgroupdiscount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='specificgroupdiscount_blockdate', to='Promotions.specificgroupdiscount')),
                ('purchasediscount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='purchasediscount_blockdate', to='Promotions.purchasediscount')),
                ('specificbrand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='specificbrand_blockdate', to='Promotions.specificbrand')),
                ('spenddiscount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='spenddiscount_blockdate', to='Promotions.spenddiscount')),
                ('spendsomeamount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='spendsomeamount_blockdate', to='Promotions.spendsomeamount')),
                ('fixedpriceservice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fixedpriceservice_blockdate', to='Promotions.fixedpriceservice')),
                ('mentionednumberservice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mentionednumberservice_blockdate', to='Promotions.mentionednumberservice')),
                ('bundlefixed', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bundlefixed_blockdate', to='Promotions.bundlefixed')),
                ('retailandservice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='retailandservice_blockdate', to='Promotions.retailandgetservice')),
                ('userrestricteddiscount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userrestricteddiscount_blockdate', to='Promotions.userrestricteddiscount')),
                ('complimentary', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complimentary_blockdate', to='Promotions.complimentarydiscount')),
                ('package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='package_blockdate', to='Promotions.packagesdiscount')),
            ],
        ),
        migrations.CreateModel(
            name='DateRestrictions',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('start_date', models.DateField(null=True, verbose_name='Start Date')),
                ('end_date', models.DateField(null=True, verbose_name='End Date')),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('directorflat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='directorflat_daterestrictions', to='Promotions.directorflatdiscount')),
                ('business_address', models.ManyToManyField(blank=True, null=True, related_name='business_address_daterestrictions', to='Business.businessaddress')),
                ('specificgroupdiscount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='specificgroupdiscount_daterestrictions', to='Promotions.specificgroupdiscount')),
                ('purchasediscount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='purchasediscount_daterestrictions', to='Promotions.purchasediscount')),
                ('specificbrand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='specificbrand_daterestrictions', to='Promotions.specificbrand')),
                ('spenddiscount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='spenddiscount_daterestrictions', to='Promotions.spenddiscount')),
                ('spendsomeamount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='spendsomeamount_daterestrictions', to='Promotions.spendsomeamount')),
                ('fixedpriceservice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fixedpriceservice_daterestrictions', to='Promotions.fixedpriceservice')),
                ('mentionednumberservice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mentionednumberservice_daterestrictions', to='Promotions.mentionednumberservice')),
                ('bundlefixed', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bundlefixed_daterestrictions', to='Promotions.bundlefixed')),
                ('retailandservice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='retailandservice_daterestrictions', to='Promotions.retailandgetservice')),
                ('userrestricteddiscount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userrestricteddiscount_daterestrictions', to='Promotions.userrestricteddiscount')),
                ('complimentary', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complimentary_daterestrictions', to='Promotions.complimentarydiscount')),
                ('package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='package_daterestrictions', to='Promotions.packagesdiscount')),
            ],
        ),
        migrations.CreateModel(
            name='DayRestrictions',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('day', models.CharField(blank=True, max_length=20, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('directorflat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='directorflat_dayrestrictions', to='Promotions.directorflatdiscount')),
                ('specificgroupdiscount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='specificgroupdiscount_dayrestrictions', to='Promotions.specificgroupdiscount')),
                ('purchasediscount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='purchasediscount_dayrestrictions', to='Promotions.purchasediscount')),
                ('specificbrand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='specificbrand_dayrestrictions', to='Promotions.specificbrand')),
                ('spenddiscount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='spenddiscount_dayrestrictions', to='Promotions.spenddiscount')),
                ('spendsomeamount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='spendsomeamount_dayrestrictions', to='Promotions.spendsomeamount')),
                ('fixedpriceservice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fixedpriceservice_dayrestrictions', to='Promotions.fixedpriceservice')),
                ('mentionednumberservice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mentionednumberservice_dayrestrictions', to='Promotions.mentionednumberservice')),
                ('bundlefixed', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bundlefixed_dayrestrictions', to='Promotions.bundlefixed')),
                ('retailandservice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='retailandservice_dayrestrictions', to='Promotions.retailandgetservice')),
                ('userrestricteddiscount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userrestricteddiscount_dayrestrictions', to='Promotions.userrestricteddiscount')),
                ('complimentary', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complimentary_dayrestrictions', to='Promotions.complimentarydiscount')),
                ('package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='package_dayrestrictions', to='Promotions.packagesdiscount')),
            ],
        ),
        migrations.CreateModel(
            name='ProductAndGetSpecific',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_productandgetspecific', to='Product.product')),
                ('retailandservice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='retailandservice_productandgetspecific', to='Promotions.retailandgetservice')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_productandgetspecific', to='Service.service')),
                ('promotion_type', models.CharField(choices=[('Brand', 'Brand'), ('Product', 'Product')], default='Product', max_length=20)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='brand_productandgetspecific', to='Product.brand')),
            ],
        ),
        migrations.CreateModel(
            name='PromotionExcludedItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('object_type', models.CharField(choices=[('Direct Or Flat', 'Direct Or Flat'), ('Specific Group Discount', 'Specific Group Discount'), ('Purchase Discount', 'Purchase Discount'), ('Specific Brand Discount', 'Specific Brand Discount'), ('Spend_Some_Amount', 'Spend_Some_Amount'), ('Fixed_Price_Service', 'Fixed_Price_Service'), ('Mentioned_Number_Service', 'Mentioned_Number_Service'), ('Bundle_Fixed_Service', 'Bundle_Fixed_Service'), ('Retail_and_Get_Service', 'Retail_and_Get_Service'), ('User_Restricted_discount', 'User_Restricted_discount'), ('Complimentary_Discount', 'Complimentary_Discount'), ('Packages_Discount', 'Packages_Discount')], default='', max_length=800)),
                ('object_id', models.CharField(default='', max_length=800)),
                ('excluded_type', models.CharField(choices=[('Product', 'Product'), ('Service', 'Service'), ('Voucher', 'Voucher')], default='', max_length=100)),
                ('excluded_id', models.CharField(default='', max_length=800)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CategoryDiscount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('discount', models.FloatField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('directorflat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='directorflat_categorydiscount', to='Promotions.directorflatdiscount')),
                ('category_type', models.CharField(blank=True, choices=[('All', 'All'), ('Service', 'Service'), ('Retail', 'Retail'), ('Voucher', 'Voucher')], max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DiscountOnFreeService',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('discount_percentage', models.FloatField(blank=True, default=0, null=True)),
                ('discount_duration', models.CharField(blank=True, choices=[('Next 1 visit', 'Next 1 visit'), ('Next 2 visit', 'Next 2 visit'), ('Next 3 visit', 'Next 3 visit'), ('Next 4 visit', 'Next 4 visit'), ('Next 5 visit', 'Next 5 visit'), ('Next 6 visit', 'Next 6 visit'), ('Next 7 visit', 'Next 7 visit'), ('Next 8 visit', 'Next 8 visit'), ('Next 9 visit', 'Next 9 visit'), ('Next 10 visit', 'Next 10 visit')], default='Next 1 visit', max_length=100, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('complimentary', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complimentary_discountonfreeservice', to='Promotions.complimentarydiscount')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_discountonfreeservice', to='Service.service')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceDurationForSpecificTime',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('service_duration', models.CharField(blank=True, max_length=100, null=True)),
                ('package_duration', models.CharField(blank=True, max_length=100, null=True)),
                ('total_amount', models.FloatField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='package_servicedurationspecifictime', to='Promotions.packagesdiscount')),
                ('service', models.ManyToManyField(blank=True, null=True, related_name='service_servicedurationspecifictime', to='Service.service')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceGroupDiscount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('discount', models.FloatField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('servicegroup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicegroup_specificgroupdiscount', to='Service.servicegroup')),
                ('specificgroupdiscount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicegroupdiscount_specificgroupdiscount', to='Promotions.specificgroupdiscount')),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='brand_specificgroupdiscount', to='Product.brand')),
                ('brand_discount', models.FloatField(blank=True, default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpendSomeAmountAndGetDiscount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('spend_amount', models.FloatField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_spendandgetdiscount', to='Service.service')),
                ('spandsomeamount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='spendandgetdiscount_spendsomeamount', to='Promotions.spendsomeamount')),
            ],
        ),
    ]
