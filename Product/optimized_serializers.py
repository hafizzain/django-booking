from django.db.models import Q
from rest_framework import serializers


from Product.Constants.index import tenant_media_base_url
from Product.models import (Category, Brand, CurrencyRetailPrice, Product, ProductMedia, ProductOrderStockReport, 
                            ProductStock, OrderStock , OrderStockProduct, ProductConsumption, ProductStockTransfer)
from Business.models import BusinessAddress, BusinessVendor
from Business.serializers.v1_serializers import BusiessAddressAppointmentSerializer

from Utility.models import Language
from Product.models import ProductTranslations


class OptimizedBrandSerializer(serializers.ModelSerializer):
    # image = serializers.SerializerMethodField()

    # def get_image(self, obj):
    #     if obj.image:
    #         try:
    #             request = self.context["request"]
    #             url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
    #             return f'{url}{obj.image}'
    #         except Exception as err:
    #             return f'{obj.image}'
    #     return None
    
    class Meta:
        model = Brand
        fields = [
            'id', 
            'name', 
            # 'description', 
            # 'website', 
            # 'image', 
            # 'is_active'
        ]


class OptimizedCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 
            'name', 
            # 'is_active', 
            # 'created_at'
        ]


class OptimizedCurrencyRetailPriceSerializer(serializers.ModelSerializer):
    currency_code = serializers.CharField(source='currency.code')
    
    # def get_currency_code(self, obj):
    #     try:
    #         return obj.currency.code
    #     except Exception as err:
    #         return str(err)
            
    class Meta:
        model = CurrencyRetailPrice
        # fields = '__all__'
        fields = [
            'id',
            'retail_price',
            'currency',
            'currency_code',
        ]


class OptimizedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name']

class OptimizedProductStockSerializer(serializers.ModelSerializer):
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
            return OptimizedLocationSerializer(loc).data
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

class OtpimizedProductSerializer(serializers.ModelSerializer):
    brand=OptimizedBrandSerializer(read_only=True)
    category= OptimizedCategorySerializer(read_only=True)
    # vendor= VendorSerializer(read_only=True)
    
    # media = serializers.SerializerMethodField()
    # stocks = serializers.SerializerMethodField(read_only=True)
    location_quantities = serializers.SerializerMethodField(read_only=True)
    cover_image = serializers.SerializerMethodField()
    # consumed = serializers.SerializerMethodField()
    # stocktransfer = serializers.SerializerMethodField()
    currency_retail_price = serializers.SerializerMethodField()
    
    # location = serializers.SerializerMethodField()
    # location = serializers.SerializerMethodField(read_only=True)
    # size = serializers.SerializerMethodField(read_only=True)

    # short_id = serializers.SerializerMethodField(read_only=True)
    # invoices = serializers.SerializerMethodField(read_only=True)

    
    # def get_short_id(self,obj):
    #     return obj.short_id

    # def get_size(self,obj):
    #     try:
    #         return obj.product_size
    #     except:
    #         return None
    
    def get_currency_retail_price(self, obj):
        location_currency_id = self.context.get('location_currency', None)

        currency_retail = CurrencyRetailPrice.objects.filter(
            product = obj,
            currency__id = location_currency_id
        )
        return OptimizedCurrencyRetailPriceSerializer( currency_retail, many = True).data
        
    # def get_stocktransfer(self, obj):
        
    #         stocktransfer = ProductStockTransfer.objects.filter(product = obj)
    #         return ProductStockTransferlocationSerializer( stocktransfer, many = True).data
        
    # def get_consumed(self, obj):
        
    #         comsumption = ProductConsumption.objects.filter(product = obj)
    #         return ProductConsumptionSerializer( comsumption, many = True).data

    
    # def get_location(self, obj):
    #     try:
    #         all_location = obj.location.all()
    #         return LocationSerializer(all_location, many = True).data
    #     except Exception as err:
    #         print(err)
    #         None

    
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


    # def get_media(self, obj):
    #     try:
    #         context = self.context
    #     except:
    #         context = {}
    #     all_medias = ProductMedia.objects.filter(product=obj, is_deleted=False).order_by('-created_at')
    #     return ProductMediaSerializer(all_medias, many=True, context=context).data

    # def get_stocks(self, obj):
    #     location = self.context['location']
    #     if location is not None:
    #         all_stocks = ProductStock.objects.filter(product=obj, is_deleted=False, location__id = location ).order_by('-created_at')
    #         return ProductStockSerializer(all_stocks, many=True).data
    #     else:
    #         all_stocks = ProductStock.objects.filter(product=obj, is_deleted=False,).order_by('-created_at')
    #         return ProductStockSerializer(all_stocks, many=True).data

    def get_location_quantities(self, obj):
        location = self.context['location']
        if location is not None:
            all_stocks = ProductStock.objects.filter(product=obj, location__is_deleted=False, location__id = location).order_by('-created_at')
            return OptimizedProductStockSerializer(all_stocks, many=True).data
        else:
            all_stocks = ProductStock.objects.filter(product=obj,
                                                     is_deleted=False,
                                                     location__is_deleted=False,
                                                     location__is_closed=False,
                                                     location__is_active=True).order_by('-created_at')
            return OptimizedProductStockSerializer(all_stocks, many=True).data
        
    # def get_invoices(self, obj):
    #     try:
    #         invoice = ProductTranslations.objects.filter(product = obj) 
    #         return ProductTranlationsSerializer(invoice, many=True).data
    #     except:
    #         return []


    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'currency_retail_price',
            'product_type',
            'description',
            'is_active',
            'cover_image',
            'location_quantities',
            'category',
            'brand', 
            'short_description',
            # 'is_active',
            # 'short_id', 
            # 'arabic_name', 
            # 'size',
            # 'cost_price',
            # 'tax_rate',
            # 'barcode_id',
            # 'sku',
            # 'slug',
            # 'media',
            # 'stocks',
            # 'vendor',
            # 'created_at',
            # 'consumed',
            # 'stocktransfer',
            # 'location',
            # 'invoices'
        ]
        read_only_fields = [
            # 'slug', 
            'id'
        ]



class OptimizedProductSerializerForInsights(serializers.ModelSerializer):
    cover_image = serializers.SerializerMethodField()
    most_transferred_products = serializers.IntegerField()
    
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


    class Meta:
        model = Product
        fields = [
            'id', 
            'name',
            'cover_image',
            'most_transferred_products'

        ]
        read_only_fields = [
            'id'
        ]


