from django.db.models import Q
from rest_framework import serializers

from Product.Constants.index import tenant_media_base_url
from Product.models import (Category, Brand, CurrencyRetailPrice, Product, ProductMedia, ProductOrderStockReport, 
                            ProductStock, OrderStock , OrderStockProduct, ProductConsumption, ProductStockTransfer)
from Business.models import BusinessAddress, BusinessVendor
from Business.serializers.v1_serializers import BusiessAddressAppointmentSerializer, BusiessAddressTransferSerializer, BusinessAddressNameSerializer

from Utility.models import Language
from Product.models import ProductTranslations

from django.db.models import Sum, FloatField
from django.db.models.functions import Coalesce




class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name']

class SaveFileSerializer(serializers.Serializer):
    
    class Meta:
        model = Product
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active', 'created_at']

class CategorySerializerForProduct(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class CategorySerializerDropdown(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class BrandSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except Exception as err:
                return f'{obj.image}'
        return None
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'website', 'image', 'is_active']


class BrandSerializerForProduct(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = ['name']


class BrandSerializerDropdown(serializers.ModelSerializer):
    
    class Meta:
        model = Brand
        fields = ['id', 'name']


class ProductMediaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context['request']
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    class Meta:
        model = ProductMedia
        fields = ['id', 'image']


class CurrencyRetailPriceSerializer(serializers.ModelSerializer):
    currency_code = serializers.SerializerMethodField(read_only=True)
    
    def get_currency_code(self, obj):
        try:
            return obj.currency.code
        except Exception as err:
            return str(err)
            
    class Meta:
        model = CurrencyRetailPrice
        fields = '__all__'        

class CurrencyRetailPriceSerializerOP(serializers.ModelSerializer):
    currency_code = serializers.SerializerMethodField(read_only=True)
    
    def get_currency_code(self, obj):
        try:
            return obj.currency.code
        except Exception as err:
            return str(err)
            
    class Meta:
        model = CurrencyRetailPrice
        fields = ['retail_price', 'currency', 'currency_code']   
        
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessVendor
        fields = '__all__'


class VendorSerializerForProduct(serializers.ModelSerializer):
    class Meta:
        model = BusinessVendor
        fields = ['vendor_name']





class ProductStockSerializer(serializers.ModelSerializer):
    current_stock = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    turnover = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    def get_turnover(self, obj):
        try:
            quantity = obj.available_quantity - obj.sold_quantity
            return 'Highest' if int(quantity) > 0 else 'Lowest' 
        except Exception as err:
            print(err)
            
    def get_status_text(self, obj):
        try:
            #quantity = obj.available_quantity - obj.sold_quantity
            return 'Highest' if int(obj.sold_quantity) > 50 else 'Lowest'
        except Exception as err:
            print(err)
            
    def get_status(self, obj):
        try:
            quantity = obj.available_quantity - obj.sold_quantity
            return 'True' if int(quantity) > 0 else 'False'
        except Exception as err:
            print(err)
    
    def get_location(self, obj):
        try:
            print(obj.location)
            loc = BusinessAddress.objects.get(id = str(obj.location), is_deleted=False )
            return LocationSerializer(loc).data
        except Exception as err:
            print(err)
            None

    def get_current_stock(self, obj):
        return obj.available_quantity

    class Meta:
        model = ProductStock
        fields = ['id', 'location', 'low_stock', 'current_stock', 'product',
                  'reorder_quantity', 'available_quantity','sold_quantity',
                  'sellable_quantity','consumable_quantity' , 'amount', 'unit' ,
                  'alert_when_stock_becomes_lowest', 'sold_quantity','turnover','status_text','status','is_active' ]
        

class ProductStockSerializerMainPage(serializers.ModelSerializer):
    turnover = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    def get_turnover(self, obj):
        try:
            quantity = obj.available_quantity - obj.sold_quantity
            return 'Highest' if int(quantity) > 0 else 'Lowest' 
        except Exception as err:
            print(err)
            
    def get_status_text(self, obj):
        try:
            #quantity = obj.available_quantity - obj.sold_quantity
            return 'Highest' if int(obj.sold_quantity) > 50 else 'Lowest'
        except Exception as err:
            print(err)
            
    def get_status(self, obj):
        try:
            quantity = obj.available_quantity - obj.sold_quantity
            return 'True' if int(quantity) > 0 else 'False'
        except Exception as err:
            print(err)

    class Meta:
        model = ProductStock
        fields = ['id', 'sold_quantity', 'available_quantity', 'turnover', 'status_text', 'status']
        

class ProductStockSerializerForProduct(serializers.ModelSerializer):
    current_stock = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    turnover = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    def get_turnover(self, obj):
        try:
            quantity = obj.available_quantity - obj.sold_quantity
            return 'Highest' if int(quantity) > 0 else 'Lowest' 
        except Exception as err:
            print(err)
            
    def get_status_text(self, obj):
        try:
            #quantity = obj.available_quantity - obj.sold_quantity
            return 'Highest' if int(obj.sold_quantity) > 50 else 'Lowest'
        except Exception as err:
            print(err)
            
    def get_status(self, obj):
        try:
            quantity = obj.available_quantity - obj.sold_quantity
            return 'True' if int(quantity) > 0 else 'False'
        except Exception as err:
            print(err)
    
    def get_location(self, obj):
        try:
            print(obj.location)
            loc = BusinessAddress.objects.get(id = str(obj.location), is_deleted=False )
            return LocationSerializer(loc).data
        except Exception as err:
            print(err)
            None

    def get_current_stock(self, obj):
        return obj.available_quantity

    class Meta:
        model = ProductStock
        fields = ['id', 'location', 'low_stock', 'current_stock', 'product',
                  'reorder_quantity', 'available_quantity','sold_quantity',
                  'sellable_quantity','consumable_quantity' , 'amount', 'unit' ,
                  'alert_when_stock_becomes_lowest', 'sold_quantity','turnover','status_text','status','is_active' ]
        

class ProductStockSerializerOP(serializers.ModelSerializer):
    current_stock = serializers.SerializerMethodField()

    def get_current_stock(self, obj):
        return obj.available_quantity

    class Meta:
        model = ProductStock
        fields = ['low_stock', 'current_stock', 'reorder_quantity']

class ProductWithStockSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    category= CategorySerializer(read_only=True)
    brand = serializers.SerializerMethodField()
    vendor= VendorSerializer(read_only=True)
    stocktransfer = serializers.SerializerMethodField()
    consumed = serializers.SerializerMethodField()
    currency_retail_price = serializers.SerializerMethodField()
    
    def get_consumed(self, obj):
        
            comsumption = ProductConsumption.objects.filter(product = obj)
            return ProductConsumptionSerializer( comsumption, many = True).data
    
    def get_currency_retail_price(self, obj):
            currency_retail = CurrencyRetailPrice.objects.filter(product = obj)
            return CurrencyRetailPriceSerializer( currency_retail, many = True).data
    
    def get_stocktransfer(self, obj):
            stocktransfer = ProductStockTransfer.objects.filter(product = obj)
            return ProductStockTransferlocationSerializer( stocktransfer, many = True).data
    
    def get_brand(self, obj):
        brand = BrandSerializer(obj.brand, read_only=True, context=self.context)
        return brand.data

    def get_stock(self, obj):
        stock = ProductStock.objects.filter(product=obj, is_deleted=False)#[0]
        return ProductStockSerializer(stock, many = True).data
        

    class Meta:
        model = Product
        fields = ['id', 'name', 'arabic_name', 'cost_price','category', 'brand', 'vendor',
                  'stock','stocktransfer','location','consumed','currency_retail_price'
                  ]
        read_only_fields = ['id']


class ProductWithStockSerializerOP(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    total_consumption = serializers.FloatField()
    total_transfer = serializers.FloatField()
    currency_retail_price = serializers.SerializerMethodField()
    total_transfer_debug = serializers.SerializerMethodField()

    def get_total_transfer_debug(self, obj):
        transfers = ProductStockTransfer.objects \
                        .filter(product=obj, is_deleted=False)
        
        return ProductStockTransferlocationSerializer(transfers, many=True).data


    def get_currency_retail_price(self, obj):
        currency_retail = obj.product_currencyretailprice \
                                .filter(product=obj) \
                                .select_related('currency')
        return CurrencyRetailPriceSerializer(currency_retail, many=True).data

    def get_stock(self, obj):
        location_id = self.context.get('location_id', None)
        query = Q(product=obj, is_deleted=False)
        if location_id:
            query &= Q(location__id=location_id)

        stock = obj.product_stock.filter(query)
        return ProductStockSerializerMainPage(stock, many = True).data

    class Meta:
        model = Product
        fields = ['id', 'name', 'stock','currency_retail_price', 'total_transfer', 'total_consumption',
                  'total_transfer_debug']
        read_only_fields = ['id']
        

class ProductStockTransferlocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStockTransfer
        fields = '__all__'
        
class ProductConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductConsumption
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    brand=BrandSerializer(read_only=True)
    category= CategorySerializer(read_only=True)
    vendor= VendorSerializer(read_only=True)
    
    media = serializers.SerializerMethodField()
    stocks = serializers.SerializerMethodField(read_only=True)
    location_quantities = serializers.SerializerMethodField(read_only=True)
    cover_image = serializers.SerializerMethodField()
    consumed = serializers.SerializerMethodField()
    stocktransfer = serializers.SerializerMethodField()
    currency_retail_price = serializers.SerializerMethodField()
    
    location = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField(read_only=True)
    size = serializers.SerializerMethodField(read_only=True)

    short_id = serializers.SerializerMethodField(read_only=True)
    invoices = serializers.SerializerMethodField(read_only=True)

    
    def get_short_id(self,obj):
        return obj.short_id

    def get_size(self,obj):
        try:
            return obj.product_size
        except:
            return None
    
    def get_currency_retail_price(self, obj):
            currency_retail = CurrencyRetailPrice.objects.filter(product = obj)
            return CurrencyRetailPriceSerializer( currency_retail, many = True).data
        
    def get_stocktransfer(self, obj):
        
            stocktransfer = ProductStockTransfer.objects.filter(product = obj)
            return ProductStockTransferlocationSerializer( stocktransfer, many = True).data
        
    def get_consumed(self, obj):
        
            comsumption = ProductConsumption.objects.filter(product = obj)
            return ProductConsumptionSerializer( comsumption, many = True).data

    
    def get_location(self, obj):
        try:
            all_location = obj.location.all()
            return LocationSerializer(all_location, many = True).data
        except Exception as err:
            print(err)
            None

    
    def get_cover_image(self, obj):
        cvr_img = ProductMedia.objects.filter(product=obj, is_cover=True, is_deleted=False).order_by('-created_at')
        try:
            if len(cvr_img) > 0 :
                cvr_img = cvr_img[0]
                request = self.context['request']
                url = tenant_media_base_url(request, is_s3_url=cvr_img.is_image_uploaded_s3)
                return f'{url}{cvr_img.image}'
        except:
            return None


    def get_media(self, obj):
        try:
            context = self.context
        except:
            context = {}
        all_medias = ProductMedia.objects.filter(product=obj, is_deleted=False).order_by('-created_at')
        return ProductMediaSerializer(all_medias, many=True, context=context).data

    def get_stocks(self, obj):
        location = self.context['location']
        if location is not None:
            all_stocks = ProductStock.objects.filter(product=obj, is_deleted=False, location__id = location ).order_by('-created_at')
            return ProductStockSerializer(all_stocks, many=True).data
        else:
            all_stocks = ProductStock.objects.filter(product=obj, is_deleted=False,).order_by('-created_at')
            return ProductStockSerializer(all_stocks, many=True).data

    def get_location_quantities(self, obj):
        location = self.context['location']
        if location is not None:
            all_stocks = ProductStock.objects.filter(product=obj, location__is_deleted=False, location__id = location).order_by('-created_at')
            return ProductStockSerializer(all_stocks, many=True).data
        else:
            all_stocks = ProductStock.objects.filter(product=obj,
                                                     is_deleted=False,
                                                     location__is_deleted=False,
                                                     location__is_closed=False,
                                                     location__is_active=True).order_by('-created_at')
            return ProductStockSerializer(all_stocks, many=True).data
        
    def get_invoices(self, obj):
        try:
            invoice = ProductTranslations.objects.filter(product = obj) 
            return ProductTranlationsSerializer(invoice, many=True).data
        except:
            return []


    class Meta:
        model = Product
        fields = [
            'id', 
            'short_id', 
            'name', 
            'arabic_name', 
            'currency_retail_price',
            'size',
            'product_type',
            'cost_price',
            'tax_rate',
            'short_description',
            'description',
            'barcode_id',
            'sku',
            'slug',
            'is_active',
            'media',
            'cover_image',
            'stocks',
            'location_quantities',
            'vendor',
            'category',
            'brand', 
            'created_at',
            'consumed',
            'stocktransfer',
            'location',
            'is_active',
            'invoices'
        ]
        read_only_fields = ['slug', 'id']


class ProductSerializerMainPage(serializers.ModelSerializer):
    brand =BrandSerializerForProduct(read_only=True)
    category = CategorySerializerForProduct(read_only=True)
    vendor = VendorSerializerForProduct(read_only=True)
    
    # media = serializers.SerializerMethodField()
    # stocks = serializers.SerializerMethodField(read_only=True)
    location_quantities = serializers.SerializerMethodField(read_only=True)
    cover_image = serializers.SerializerMethodField()
    consumed = serializers.SerializerMethodField()
    stocktransfer = serializers.SerializerMethodField()
    currency_retail_price = serializers.SerializerMethodField()
    
    
    def get_currency_retail_price(self, obj):
        currency_retail = list(obj.product_currencyretailprice.values('currency', 'retail_price'))
        return currency_retail
        
    def get_stocktransfer(self, obj):
        stocktransfer = list(obj.products_stock_transfers.values('quantity'))
        return stocktransfer
        
    def get_consumed(self, obj):
        consumption = list(obj.consumptions.values('location', 'quantity'))
        return consumption
    
    def get_cover_image(self, obj):
        cvr_img = ProductMedia.objects.filter(product=obj, is_cover=True, is_deleted=False).order_by('-created_at')
        try:
            if len(cvr_img) > 0 :
                cvr_img = cvr_img[0]
                request = self.context['request']
                url = tenant_media_base_url(request, is_s3_url=cvr_img.is_image_uploaded_s3)
                return f'{url}{cvr_img.image}'
        except:
            return None

    def get_location_quantities(self, obj):
        location = self.context['location']
        if location is not None:
            all_stocks = list(obj.product_stock.filter(
                                                  location__is_deleted=False,
                                                  location__id = location) \
                                                .values('location', 'available_quantity'))
            
            return all_stocks
        else:
            all_stocks = list(obj.product_stock.filter(
                                                     is_deleted=False,
                                                     location__is_deleted=False,
                                                     location__is_closed=False,
                                                     location__is_active=True) \
                                                .values('location', 'available_quantity'))
                                                
                                                
            return all_stocks


    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'currency_retail_price',
            'barcode_id',
            'cover_image',
            'location_quantities',
            'vendor',
            'category',
            'brand', 
            'consumed',
            'stocktransfer',
            'is_active',
        ]
        read_only_fields = ['slug', 'id']

class ProductSerializerDropDown(serializers.ModelSerializer):

    brand = BrandSerializer(read_only=True)    

    location_quantities = serializers.SerializerMethodField(read_only=True)

    def get_location_quantities(self, obj):
        location = self.context['location']
        if location is not None:
            all_stocks = ProductStock.objects.filter(product=obj, location__is_deleted=False, location__id = location).order_by('-created_at')
            return ProductStockSerializerOP(all_stocks, many=True).data
        else:
            all_stocks = ProductStock.objects.filter(product=obj,
                                                     is_deleted=False,
                                                     location__is_deleted=False,
                                                     location__is_closed=False,
                                                     location__is_active=True).order_by('-created_at')
            return ProductStockSerializerOP(all_stocks, many=True).data
        
    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'location_quantities']

class ProductTranlationsSerializerNew(serializers.ModelSerializer):
    
    class Meta:
        model = ProductTranslations
        fields = [
            'id', 
            'product', 
            'product_name',
            'language'
            ]

class ProductTranlationsSerializer(serializers.ModelSerializer):
    
    invoiceLanguage = serializers.SerializerMethodField(read_only=True)
    def get_invoiceLanguage(self, obj):
        language = Language.objects.get(id__icontains = obj.language)
        return language.id
        
    
    class Meta:
        model = ProductTranslations
        fields = [
            'id', 
            'product', 
            'product_name',
            'invoiceLanguage'
            ]

class ProductOrderSerializer(serializers.ModelSerializer):
    avaiable = serializers.SerializerMethodField()
    retail_price = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    
    def get_brand(self, obj):
        try:
            return obj.brand.name
        except Exception as err:
            return None
    
    def get_avaiable(self, obj):
            quantity = ProductStock.objects.filter(product = obj)
            return ProductStockSerializer(quantity, many = True).data

            
    def get_retail_price(self, obj):
            quantity = CurrencyRetailPrice.objects.filter(product = obj)#.order_by('-created_at').distinct()
            return CurrencyRetailPriceSerializer( quantity, many = True).data
            
    class Meta:
        model = Product
        fields = '__all__'


class ProductOrderForOrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']
        
class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductOrderSerializer()
    class Meta:
        model = OrderStockProduct
        fields = ['id', 'order', 'quantity','rec_quantity', 'product', 'status', 'note', 'is_finished']


class OrderProductForOrderSerializer(serializers.ModelSerializer):
    product = ProductOrderForOrderProductSerializer()

    class Meta:
        model = OrderStockProduct
        fields = ['id', 'quantity','rec_quantity', 'product', 'status', 'is_finished']

class OrderSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(read_only=True)
    location_name = serializers.SerializerMethodField(read_only=True)
    to_location_name = serializers.SerializerMethodField(read_only=True)
    vendor_name = serializers.SerializerMethodField(read_only=True)
    
    def get_vendor_name(self, obj):
        try:
            return obj.vendor.vendor_name
        except Exception as err:
            return None
    def get_location_name(self, obj):
        try:
            return obj.from_location.address_name
        except Exception as err:
            return None
        
    def get_to_location_name(self, obj):
        try:
            return obj.to_location.address_name
        except Exception as err:
            return None
    
    
    def get_products(self, obj):
        data = OrderStockProduct.objects.filter(order=obj)
        return OrderProductSerializer(data, many=True).data
    
    class Meta:
        model= OrderStock
        fields=('id','business','vendor','to_location','from_location','to_location_name',
                'status','vendor_name','location_name','products', 'created_at')

class OrderSerializerMainPage(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(read_only=True)
    to_location_name = serializers.SerializerMethodField(read_only=True)
    vendor_name = serializers.SerializerMethodField(read_only=True)
    
    def get_vendor_name(self, obj):
        try:
            return obj.vendor.vendor_name
        except Exception as err:
            return None
        
    def get_to_location_name(self, obj):
        try:
            return obj.to_location.address_name
        except Exception as err:
            return None
    
    
    def get_products(self, obj):
        orderstockproduct = obj.order_stock.select_related('product')
        return OrderProductForOrderSerializer(orderstockproduct, many=True).data
    
    class Meta:
        model = OrderStock
        fields=('id', 'vendor','to_location', 'to_location_name',
                'status','vendor_name', 'products')


class ProductConsumptionSerializer(serializers.ModelSerializer):

    product = ProductOrderForOrderProductSerializer()
    location = BusiessAddressAppointmentSerializer()
    class Meta:
        model = ProductConsumption
        fields = ['id', 'location', 'product', 'quantity']
                            

class ProductStockTransferSerializer(serializers.ModelSerializer):

    product = ProductOrderForOrderProductSerializer()
    from_location = BusiessAddressTransferSerializer()
    to_location = BusiessAddressTransferSerializer()
    created_at = serializers.DateTimeField(format="%d-%m-%Y")
    
    class Meta:
        model = ProductStockTransfer
        fields = ['id', 'from_location', 'to_location', 'product', 'quantity','note', 'created_at']
class ProductOrderStockReportSerializer(serializers.ModelSerializer):
    
    from_location = BusiessAddressAppointmentSerializer()
    to_location = BusiessAddressAppointmentSerializer()
    location = BusiessAddressAppointmentSerializer()
    consumed_location = BusiessAddressAppointmentSerializer()
    vendor_name = serializers.SerializerMethodField(read_only=True)
    product = ProductOrderSerializer()
    
    def get_vendor_name(self, obj):
        try:
            return obj.vendor.vendor_name
        except Exception as err:
            return None
    
    class Meta:
        model = ProductOrderStockReport
        exclude = ('is_active','is_deleted', 'user')
    


class ProductStockReport_OrderStockReportsSerializer(serializers.ModelSerializer):
    
    from_location = BusinessAddressNameSerializer()
    to_location = BusinessAddressNameSerializer()
    location = BusinessAddressNameSerializer()
    consumed_location = BusinessAddressNameSerializer()
    vendor_name = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField()


    def get_created_at(self, report_instance):
        return f'{report_instance.created_at.strftime("%Y-%m-%d")}'

    def get_vendor_name(self, obj):
        try:
            return obj.vendor.vendor_name
        except Exception as err:
            return None

    class Meta:
        model = ProductOrderStockReport
        fields = ['id', 'from_location', 'to_location', 'quantity', 'location', 
                  'consumed_location', 'report_choice', 'quantity', 'created_at', 'vendor_name',
                  'before_quantity', 'after_quantity', 'reorder_quantity'
                  ]
        

class ProductStockReport_OrderStockReportsSerializerDebug(serializers.ModelSerializer):
    

    class Meta:
        model = ProductOrderStockReport
        fields = '__all__'
    


class ProductStockReportSerializer(serializers.ModelSerializer):
    retail_price = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    reports = serializers.SerializerMethodField()
    current_stock = serializers.FloatField()
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, product_instance):
        return f'{product_instance.created_at.strftime("%Y-%m-%d")}'

    
    def get_brand(self, obj):
        try:
            return obj.brand.name
        except Exception as err:
            return None
            
    def get_retail_price(self, obj):
        currency_id = self.context.get('location_currency_id')

        product_retails_ = obj.product_currencyretailprice.filter(
            currency__id = currency_id,
            is_deleted = False
        ).select_related(
            'currency'
        )

        if len(product_retails_) > 0 :
            retail_price_instance = product_retails_[0]
            return CurrencyRetailPriceSerializerOP(retail_price_instance).data
        
        return {}

    def get_reports(self, product_instance):
        report_type = self.context.get('report_type', None)
        location_id = self.context.get('location_id', None)

        query = Q(product=product_instance, location__id=location_id)

        if report_type:
            query &= Q(report_choice=report_type)

            if report_type == 'Transfer_From':
                query &= Q(from_location__id=location_id)
            elif report_type == 'Transfer_To':
                query &= Q(to_location__id=location_id)

        product_reports = ProductOrderStockReport.objects.filter(query).select_related(
            'location',
            'consumed_location',
            'from_location',
            'to_location',
            'vendor'
        )
        
        serialized_data = ProductStockReport_OrderStockReportsSerializer(product_reports, many=True)
        return serialized_data.data
            
    class Meta:
        model = Product
        fields = ['id', 'name', 'arabic_name', 'retail_price', 'current_stock', 'brand', 'cost_price', 'created_at',
                  'reports']


class ProductInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'top_sold_orders', 'arabic_name']

class ProductInventoryStockSerializer(serializers.ModelSerializer):
    current_stock = serializers.SerializerMethodField()

    def get_current_stock(self, obj):
        return obj.available_quantity

    class Meta:
        model = ProductStock
        fields = ['current_stock']