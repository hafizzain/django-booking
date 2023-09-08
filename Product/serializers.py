

from rest_framework import serializers
from Product.Constants.index import tenant_media_base_url
from Product.models import (Category, Brand, CurrencyRetailPrice, Product, ProductMedia, ProductOrderStockReport, 
                            ProductStock, OrderStock , OrderStockProduct, ProductConsumption, ProductStockTransfer)
from Business.models import BusinessAddress, BusinessVendor
from django.conf import settings
from Business.serializers.v1_serializers import BusiessAddressAppointmentSerializer

from Utility.models import  ExceptionRecord
from django.db.models import Avg, Count, Min, Sum, Q
from Utility.models import Language
from Product.models import ProductTranslations



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
        
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessVendor
        fields = '__all__'

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
            #loc = obj.location.all()
            return LocationSerializer(loc).data
            # return EmployeeServiceSerializer(obj.services).data
        except Exception as err:
            print(err)
            None

    def get_current_stock(self, obj):
        return obj.available_quantity
        # try:
        #     return obj.available_quantity - obj.sold_quantity
        # except Exception as err:
        #     ExceptionRecord.objects.create(
        #     is_resolved = True, 
        #     text= f'{str(err)}'
        # )

    class Meta:
        model = ProductStock
        fields = ['id', 'location', 'low_stock', 'current_stock', 'product',
                  'reorder_quantity', 'available_quantity','sold_quantity',
                  'sellable_quantity','consumable_quantity' , 'amount', 'unit' ,
                  'alert_when_stock_becomes_lowest', 'sold_quantity','turnover','status_text','status','is_active' ]

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
    
    #transfer_quantity = serializers.SerializerMethodField(read_only=True)
    
    # def get_transfer_quantity(self, obj):
    #     try:
    #         return Sum(ProductStockTransfer.objects.filter(product = obj.product).values_list('quantity'))
    #     except Exception as err:
    #         ExceptionRecord.objects.create(
    #             text = f"Product quantity issue {str(err)}"
    #         ) 
    
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
        
        # total_qant = 0
        # try:
        #     if stock.product.product_type == 'SELABLE':
        #         total_qant = stock.sellable_quantity 
        #     elif stock.product.product_type == 'COMSUME' :
        #         total_qant = stock.consumable_quantity
        #     else:
        #         total_qant = int(stock.sellable_quantity) + int(stock.consumable_quantity)

            
        # except Exception as err:
        #     print(err)
        # #print(type(available_quantity))
        # #print(int(available_quantity[0]))
        # available_quantity = total_qant -  stock.sold_quantity,
        # return {            
        #     'id' : stock.id,
        #     'available_stock' : int(available_quantity[0]),
        #     'quantity' : stock.sellable_quantity,
        #     'sold_stock' : stock.sold_quantity,
        #     'price' : stock.product.sell_price,
        #     'usage' : (int(total_qant) // int(stock.sold_quantity)) * 100 if stock.sold_quantity > 0 else 100,
        #     'status' : True if int(available_quantity[0]) > 0 else False,
        #     'status_text' : 'In Stock' if int(available_quantity[0]) > 0 else 'Out of stock',
        #     'sale_status' : 'High',
        #     'turnover' : 'Highest' if int(available_quantity[0]) > 0 else 'Lowest' ,
        # }
        

    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'arabic_name', 
            'cost_price',
            'category', 
            'brand', 
            'vendor',
            'stock',
            'stocktransfer',
            'location',
            'consumed',
            'currency_retail_price',
            
        ]
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
            # return EmployeeServiceSerializer(obj.services).data
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
            #'full_price',
            #'sell_price',
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
        
class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductOrderSerializer()

    class Meta:
        model = OrderStockProduct
        fields = ['id', 'order', 'quantity','rec_quantity', 'product', 'status', 'note', 'is_finished']

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


class ProductConsumptionSerializer(serializers.ModelSerializer):

    product = ProductOrderSerializer()
    location = BusiessAddressAppointmentSerializer()
    class Meta:
        model = ProductConsumption
        fields = ['id', 'location', 'product', 'quantity']
                            

class ProductStockTransferSerializer(serializers.ModelSerializer):

    product = ProductOrderSerializer()
    from_location = BusiessAddressAppointmentSerializer()
    to_location = BusiessAddressAppointmentSerializer()
    
    # transfer_quantity = serializers.SerializerMethodField(read_only=True)
    
    # def get_transfer_quantity(self, obj):
    #     try:
    #         return Sum(ProductStockTransfer.objects.filter(product = obj.product).values_list('quantity'))
    #     except Exception as err:
    #         ExceptionRecord.objects.create(
    #             text = f"Product quantity issue {str(err)}"
    #         ) 
    class Meta:
        model = ProductStockTransfer
        fields = ['id', 'from_location', 'to_location', 'product', 'quantity','note']
class ProductOrderStockReportSerializer(serializers.ModelSerializer):
    
    from_location = BusiessAddressAppointmentSerializer()
    to_location = BusiessAddressAppointmentSerializer()
    location = BusiessAddressAppointmentSerializer()
    consumed_location = BusiessAddressAppointmentSerializer()
    vendor_name = serializers.SerializerMethodField(read_only=True)
    product = ProductOrderSerializer()
    # stocks = serializers.SerializerMethodField(read_only=True)
    
    def get_vendor_name(self, obj):
        try:
            return obj.vendor.vendor_name
        except Exception as err:
            return None
    
    # def get_stocks(self, obj):
    #     location = self.context.get('location')
    #     if location is not None:
    #         all_stocks = ProductStock.objects.filter(product=obj, is_deleted=False, location__id=location).order_by('-created_at')
    #     else:
    #         all_stocks = ProductStock.objects.filter(product=obj, is_deleted=False).order_by('-created_at')
    #     return ProductStockSerializer(all_stocks, many=True).data
    

    class Meta:
        model = ProductOrderStockReport
        #fields = '__all__'#['id', 'from_location', 'to_location', 'product', 'quantity','note']
        exclude = ('is_active','is_deleted', 'user')
    


class ProductStockReport_OrderStockReportsSerializer(serializers.ModelSerializer):
    
    from_location = BusiessAddressAppointmentSerializer()
    to_location = BusiessAddressAppointmentSerializer()
    location = BusiessAddressAppointmentSerializer()
    consumed_location = BusiessAddressAppointmentSerializer()
    vendor_name = serializers.SerializerMethodField(read_only=True)
    # product = ProductOrderSerializer()
    # stocks = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField()
    short_id = serializers.SerializerMethodField()

    def get_short_id(self, report_instance):
        return f'{report_instance.short_id}'


    def get_created_at(self, report_instance):
        return f'{report_instance.created_at.strftime("%Y-%m-%d")}'

    def get_vendor_name(self, obj):
        try:
            return obj.vendor.vendor_name
        except Exception as err:
            return None
    
    # def get_stocks(self, obj):
    #     location = self.context.get('location')
    #     if location is not None:
    #         all_stocks = ProductStock.objects.filter(product=obj, is_deleted=False, location__id=location).order_by('-created_at')
    #     else:
    #         all_stocks = ProductStock.objects.filter(product=obj, is_deleted=False).order_by('-created_at')
    #     return ProductStockSerializer(all_stocks, many=True).data
    

    class Meta:
        model = ProductOrderStockReport
        fields = [
            'id', 
            'from_location', 
            'to_location', 
            'quantity', 
            'short_id', 
            'location', 
            'consumed_location', 
            'vendor_name', 
            'report_choice', 
            'quantity', 
            'before_quantity', 
            'after_quantity', 
            'reorder_quantity', 
            'created_at', 
            'vendor', 
        ]
        # exclude = ('is_active','is_deleted', 'user')
    


class ProductStockReportSerializer(serializers.ModelSerializer):
    # avaiable = serializers.SerializerMethodField()
    retail_price = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    reports = serializers.SerializerMethodField()

    current_stock = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, product_instance):
        return f'{product_instance.created_at.strftime("%Y-%m-%d")}'

    def get_current_stock(self, product_instance):
        location_id = self.context.get('location_id')
        stock = ProductStock.objects.get(product=product_instance, location = location_id, is_deleted=False)#[0]
        return stock.available_quantity
    
    def get_brand(self, obj):
        try:
            return obj.brand.name
        except Exception as err:
            return None
    
    # def get_avaiable(self, obj):
    #         quantity = ProductStock.objects.filter(product = obj)
    #         return ProductStockSerializer(quantity, many = True).data

            
    def get_retail_price(self, obj):
        currency_id = self.context.get('location_currency_id')

        product_retails_ = CurrencyRetailPrice.objects.filter(
            product = obj,
            currency__id = currency_id,
            is_deleted = False
        )

        if len(product_retails_) > 0 :
            retail_price_instance = product_retails_[0]
            return CurrencyRetailPriceSerializer(retail_price_instance).data
        
        return {}

    def get_reports(self, product_instance):
        filter_query = {}
        report_type = self.context.get('report_type', None)
        location_id = self.context.get('location_id', None)

        if report_type:
            filter_query['report_choice'] = report_type

        product_reports = ProductOrderStockReport.objects.filter(
            Q(report_choice = 'Transfer_from', from_location__id = location_id) |
            Q(report_choice = 'Transfer_to', to_location__id = location_id) |
            Q(report_choice__in = ['Purchase', 'Consumed', 'Sold']),
            product = product_instance,
            **filter_query
        ).order_by('-created_at')
        
        serialized_data = ProductStockReport_OrderStockReportsSerializer(product_reports, many=True)
        return serialized_data.data
            
    class Meta:
        model = Product
        fields = ['id', 'name', 'arabic_name', 'retail_price', 'brand', 'reports', 'current_stock', 'cost_price', 'created_at']
        #  'avaiable',


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