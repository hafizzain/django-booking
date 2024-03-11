from Appointment.serializers import UpdateAppointmentSerializer
from rest_framework import serializers
from Appointment.models import AppointmentCheckout, AppointmentService, AppointmentEmployeeTip
from Client.models import Client, Membership

from Employee.models import Employee, EmployeeProfessionalInfo, EmployeeSelectedService
from Business.models import BusinessAddress, BusinessTax
from Order.models import Checkout, MemberShipOrder, Order, ProductOrder, ServiceOrder, VoucherOrder
from Product.Constants.index import tenant_media_base_url, tenant_media_domain
from Promotions.models import Coupon
from Utility.models import Currency, ExceptionRecord
from Sale.Constants.Promotion import get_promotions

from django.db.models import Sum, Q, Case, When
from Service.models import PriceService, Service, ServiceGroup
from Invoices.models import SaleInvoice
from django.db.models import F, FloatField
from django.db.models.functions import Coalesce
from Product.models import Product
from Service.models import Service, ServiceTranlations
from Utility.models import Language
from Product.serializers import ProductTranlationsSerializerNew
from Service.serializers import ServiceTranslationsSerializer
from MultiLanguage.models import InvoiceTranslation
from SaleRecords.models import SaleRecordsProducts


class PriceServiceSerializers(serializers.ModelSerializer):
    currency_name = serializers.SerializerMethodField(read_only=True)
    location_id = serializers.SerializerMethodField(read_only=True)

    def get_location_id(self, obj):
        try:
            return BusinessAddress.objects.get(
                currency=obj.currency
            ).id
        except:
            return None

    def get_currency_name(self, obj):
        try:
            currency = Currency.objects.get(id=obj.currency.id)
            return currency.code
        except Exception as err:
            return str(err)

    class Meta:
        model = PriceService
        fields = '__all__'


class AvailPriceServiceSerializers(serializers.ModelSerializer):
    currency_name = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)

    def get_service(self, obj):
        try:
            service = Service.objects.get(id=obj.service.id)
            return service.code
        except Exception as err:
            return str(err)

    def get_currency_name(self, obj):
        try:
            currency = Currency.objects.get(id=obj.currency.id)
            return currency.code
        except Exception as err:
            return str(err)

    class Meta:
        model = PriceService
        fields = ['id', 'currency', 'service']


class ServiceSearchSerializer(serializers.ModelSerializer):
    priceservice = serializers.SerializerMethodField(read_only=True)
    employees = serializers.SerializerMethodField(read_only=True)

    def get_employees(self, obj):
        emp = EmployeeSelectedService.objects.filter(service=obj)
        return EmployeeSelected_TenantServiceSerializer(emp, many=True, context=self.context).data

    def get_priceservice(self, obj):
        try:
            ser = PriceService.objects.filter(service=obj).order_by('-created_at')
            return PriceServiceSerializers(ser, many=True).data
        except Exception as err:
            pass

    class Meta:
        model = Service
        fields = ['id', 'name', 'arabic_name', 'location', 'client_can_book', 'employees', 'priceservice',
                  'slot_availible_for_online']


class ServiceSerializerForServiceGroup(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name']


class ServiceSearchSerializerForServiceGroup(serializers.ModelSerializer):
    priceservice = serializers.SerializerMethodField(read_only=True)

    def get_priceservice(self, obj):
        location = BusinessAddress.objects.get(id=self.context['location_id'])
        currency = location.currency
        try:
            ser = PriceService.objects.filter(service=obj, currency=currency).order_by('-created_at')
            return PriceServiceSerializers(ser, many=True).data
        except Exception as err:
            pass

    class Meta:
        model = Service
        fields = ['id', 'name', 'location', 'client_can_book', 'priceservice', 'slot_availible_for_online']


class ServiceGroupOP(serializers.ModelSerializer):
    class Meta:
        model = ServiceGroup
        fields = ['id', 'name']


class ServiceGroupSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)

    def get_status(self, obj):
        return obj.is_active

    def get_services(self, obj):
        all_service = obj.services.filter(is_deleted=False)
        # ser = Service.objects.get(id = obj.services)
        return ServiceSearchSerializer(all_service, many=True, context=self.context).data
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None

    class Meta:
        model = ServiceGroup
        fields = ['id', 'business', 'name', 'services', 'status', 'allow_client_to_select_team_member','image']


class ServiceGroupSerializerMainPage(serializers.ModelSerializer):
    services = ServiceSerializerForServiceGroup(many=True)
    image = serializers.SerializerMethodField(read_only=True)

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None
    class Meta:
        model = ServiceGroup
        fields = ['id', 'business', 'name', 'services', 'is_active','image', 'is_deleted']


class ServiceGroupSerializerOptimized(serializers.ModelSerializer):
    services = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    def get_status(self, obj):
        return obj.is_active

    def get_services(self, obj):
        all_service = obj.services.filter(is_deleted=False)
        # ser = Service.objects.get(id = obj.services)
        return ServiceSearchSerializerForServiceGroup(all_service, many=True, context=self.context).data

    class Meta:
        model = ServiceGroup
        fields = ['id', 'business', 'name', 'services', 'status', 'allow_client_to_select_team_member']


class ServiceGroupSerializerOP(serializers.ModelSerializer):
    class Meta:
        model = ServiceGroup
        fields = ['id', 'name']


class ServiceGroup_TenantSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    def get_status(self, obj):
        return obj.is_active

    def get_services(self, obj):
        all_service = obj.services.all()
        # ser = Service.objects.get(id = obj.services)
        return ServiceSearchSerializerForServiceGroup(all_service, many=True).data

    class Meta:
        model = ServiceGroup
        fields = ['id', 'business', 'name', 'services', 'status', 'allow_client_to_select_team_member']


class LocationSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()

    def get_currency(self, obj):
        return f'{obj.currency.code}'

    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name', 'currency']


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'full_name']


class MemberSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'image']


class MemberlocationSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()

    def get_location(self, obj):
        try:
            # ser = BusinessAddress.objects.filter(id = obj.location).filter(service = obj).first()
            all_location = obj.location.filter(is_deleted=False).first()
            return LocationSerializer(all_location).data
        except Exception as err:
            return str(err)

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'location']


class EmployeeSelectedServiceSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    def get_location(self, obj):
        # def get_location(self, obj):
        try:
            all_location = obj.employee.location.filter(is_deleted=False).first()
            return LocationSerializer(all_location).data
        except Exception as err:
            return str(err)
        # try:
        #     ser = Employee.objects.get(id = obj.employee.id)
        #     return MemberlocationSerializer(ser).data
        # except Exception as err:
        #     return str(err)

    def get_full_name(self, obj):
        return obj.employee.full_name

    def get_designation(self, obj):
        try:
            emp = EmployeeProfessionalInfo.objects.get(employee=obj.employee.id)
            return emp.designation
        except Exception as err:
            print(err)

    def get_image(self, obj):
        try:
            img = Employee.objects.get(id=obj.employee.id)
            if img.image:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=img.is_image_uploaded_s3)
                return f'{url}{img.image}'
            else:
                return None
        except Exception as err:
            print(str(err))

    class Meta:
        model = EmployeeSelectedService
        fields = ['id', 'service', 'employee', 'level', 'full_name', 'designation', 'image', 'location']


class EmployeeSelectedServiceSerializerOP(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'full_name']


class EmployeeSelected_TenantServiceSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    def get_location(self, obj):
        try:
            all_location = obj.employee.location.filter(is_deleted=False).first()
            return LocationSerializer(all_location).data
        except Exception as err:
            return str(err)

    def get_full_name(self, obj):
        return obj.employee.full_name

    def get_status(self, obj):
        return obj.employee.is_active

    def get_designation(self, obj):
        try:
            emp = EmployeeProfessionalInfo.objects.get(employee=obj.employee.id)
            return emp.designation
        except Exception as err:
            print(err)

    def get_image(self, obj):
        try:
            tenant = self.context["tenant"]
            img = Employee.objects.get(id=obj.employee.id)
            url = tenant_media_domain(tenant, is_s3_url=img.is_image_uploaded_s3)
            return f'{url}{img.image}'
        except Exception as err:
            print(str(err))

    class Meta:
        model = EmployeeSelectedService
        fields = ['id', 'service', 'employee', 'level', 'full_name', 'designation', 'image', 'status', 'location']


class Employee_TenantServiceSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    def get_location(self, obj):
        try:
            ser = BusinessAddress.objects.filter(id=obj.employee.location.id)[0]
            return LocationSerializer(ser).data
        except Exception as err:
            pass

    def get_full_name(self, obj):
        return obj.employee.full_name

    def get_designation(self, obj):
        try:
            emp = EmployeeProfessionalInfo.objects.get(employee=obj.employee.id)
            return emp.designation
        except Exception as err:
            print(err)

    def get_image(self, obj):
        try:
            request = self.context["request"]
            img = Employee.objects.get(id=obj.employee.id)
            url = tenant_media_base_url(request, is_s3_url=img.is_image_uploaded_s3)
            return f'{url}{img.image}'
        except Exception as err:
            print(str(err))

    class Meta:
        model = EmployeeSelectedService
        fields = ['id', 'service', 'employee', 'level', 'full_name', 'designation', 'image', 'location']


class LocationServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        # fields = '__all__'
        exclude = ['is_primary', 'is_active', 'is_closed', 'is_deleted', 'created_at', 'user', 'business',
                   'is_email_verified', 'is_mobile_verified']


class LocationServiceSerializerOP(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name']


class ServiceSerializerDropdown(serializers.ModelSerializer):
    service_group = serializers.SerializerMethodField(read_only=True)

    def get_service_group(self, obj):
        try:
            group = ServiceGroup.objects.filter(services=obj, is_deleted=False)
            return ServiceGroupOP(group, many=True).data
        except Exception as err:
            print(str(err))
            pass

    class Meta:
        model = Service
        fields = ['id', 'name', 'service_group']


class ServiceSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    employees = serializers.SerializerMethodField(read_only=True)
    service_group = serializers.SerializerMethodField(read_only=True)
    total_orders = serializers.IntegerField(read_only=True)
    priceservice = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)

    invoices = serializers.SerializerMethodField(read_only=True)

    def get_price(self, obj):
        try:
            ser = PriceService.objects.filter(service=obj).order_by('-created_at').first()
            return ser.price
        except Exception as err:
            pass
            # print(err)
            
    def get_image(self, obj):   # get client image url from AWS 
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None
    
    def get_priceservice(self, obj):

        try:
            ser = PriceService.objects.filter(service=obj).order_by('-created_at')
            return PriceServiceSerializers(ser, many=True).data
        except Exception as err:
            pass

        context = self.context
        is_mobile = context.get('is_mobile', None)

        queries = {}

        if is_mobile is not None:
            currency_code = context.get('currency_code', None)
            if currency_code is not None:
                queries['currency__code'] = currency_code

        try:
            ser = PriceService.objects.filter(
                service=obj,
                **queries
            ).order_by('-created_at')
            return PriceServiceSerializers(ser, many=True).data
        except Exception as err:
            pass

    def get_service_group(self, obj):
        try:
            group = ServiceGroup.objects.filter(services=obj, is_deleted=False)
            return ServiceGroupSerializer(group, many=True).data
        except Exception as err:
            print(str(err))
            pass

    def get_employees(self, obj):
        emp = EmployeeSelectedService.objects.filter(service=obj, employee__is_deleted=False)
        return EmployeeSelectedServiceSerializer(emp, many=True, context=self.context).data

    def get_location(self, obj):
        # loc = BusinessAddress.objects.filter(is_deleted = False)
        locations = obj.location.filter(is_deleted=False)
        return LocationServiceSerializer(locations, many=True, ).data

    # employee = EmployeeServiceSerializer(read_only=True, many = True)

    def get_invoices(self, obj):
        try:
            invoice = ServiceTranlations.objects.filter(service=obj)
            return ServiceTranlationsSerializer(invoice, many=True).data
        except:
            return []

    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'arabic_name',
            'service_availible',
            'employees',
            'parrent_service',
            'description',
            'price',
            'location',
            'controls_time_slot',
            'initial_deposit',
            'client_can_book',
            'slot_availible_for_online',
            'is_package',
            'service_group',
            'priceservice',
            'enable_team_comissions',
            'enable_vouchers',
            'invoices',
            'total_orders',
            'image',
        ]


class ServiceSerializerMainpage(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    employees = serializers.SerializerMethodField(read_only=True)
    service_group = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)

    def get_price(self, obj):
    
        ser = obj.service_priceservice.order_by('-created_at').first()
        if ser:
            return ser.price
        else:
            return None

    def get_service_group(self, obj):
        group = obj.servicegroup_services.filter(is_deleted=False)
        return ServiceGroupSerializerOP(group, many=True).data

    def get_employees(self, obj):
        emp_ids = obj.employee_service.filter(employee__is_deleted=False).values_list('employee__id', flat=True)
        employees = Employee.objects.filter(id__in=emp_ids)
        return EmployeeSelectedServiceSerializerOP(employees, many=True, context=self.context).data

    def get_location(self, obj):
        locations = obj.location.filter(is_deleted=False)
        return LocationServiceSerializerOP(locations, many=True, ).data
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None

    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'employees',
            'price',
            'location',
            'service_group',
            'image',
        ]


class ServiceSerializerOP(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    priceservice = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    avaliableservicegroup = serializers.SerializerMethodField(read_only=True)
    avaliablesobj = serializers.SerializerMethodField(read_only=True)

    def get_price(self, obj):
        try:
            ser = PriceService.objects.filter(service=obj).order_by('-created_at').first()
            return ser.price
        except Exception as err:
            pass
            # print(err)
            
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None

    def get_priceservice(self, obj):
        is_mobile = self.context.get('is_mobile', None)
        currency_code = self.context.get('currency_code', None)
        query = Q(service=obj)

        if currency_code is not None:
            query &= Q(currency__code=currency_code)

        try:
            ser = PriceService.objects.filter(query).order_by('-created_at')
            return PriceServiceSerializers(ser, many=True).data
        except Exception as err:
            pass

    def get_avaliableservicegroup(self, obj):
        group = obj.servicegroup_services.filter(is_deleted=False)
        return ServiceGroupSerializerOP(group, many=True).data

    def get_avaliablesobj(self, obj):
        all_obj = []
        all_obj.append(obj.id)
        return all_obj

    class Meta:
        model = Service
        fields = ['id', 'name', 'price', 'controls_time_slot', 'client_can_book', 'slot_availible_for_online',
                  'priceservice', 'avaliableservicegroup', 'avaliablesobj', 'image']


class ServiceTranlationsSerializer(serializers.ModelSerializer):
    invoiceLanguage = serializers.SerializerMethodField(read_only=True)

    def get_invoiceLanguage(self, obj):
        language = Language.objects.get(id__icontains=obj.language)
        return language.id

    class Meta:
        model = ServiceTranlations
        fields = [
            'id',
            'service',
            'service_name',
            'invoiceLanguage'
        ]


class POSerializerForClientSale(serializers.ModelSerializer):
    
    member = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)
    product_details = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        return obj.product.name if obj.product.name else None

    def get_price(self, obj):
        return obj.price

    def get_product_details(self, obj):
        return obj.product.description if obj.product.description else None

    def get_order_type(self, obj):
        return 'Product'

    def get_product_name(self, obj):
        return obj.product.name

    def get_member(self, obj):
      
        return obj.employee.full_name
        

    class Meta:
        model = SaleRecordsProducts
        fields = ['quantity', 'member', 'created_at', 'tip', 'payment_type', 'price',
                  'name', 'product_name', 'gst', 'order_type', 'product_details']


class ProductOrderSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)
    product_details = serializers.SerializerMethodField(read_only=True)
    product_price = serializers.SerializerMethodField(read_only=True)

    price = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    total_product = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        try:
            return obj.product.name
        except Exception as err:
            return None

    def get_total_product(self, obj):
        try:
            return obj.checkout.total_product_price
        except:
            return 0

    def get_price(self, obj):
        try:
            return obj.current_price
        except Exception as err:
            return None

    # item_sold = serializers.SerializerMethodField(read_only=True)

    # def get_item_sold(self, obj):
    #     try:
    #         product_stck =ProductStock.objects.get(product = obj)
    #         return product_stck.sold_quantity
    #     except Exception as err:
    #         print(err)
    def get_product_details(self, obj):
        try:
            return obj.product.description
        except Exception as err:
            return None

    def get_product_price(self, obj):
        try:
            return obj.current_price
        except Exception as err:
            return None

    def get_order_type(self, obj):
        return 'Product'

    def get_product_name(self, obj):
        try:
            return obj.product.name
        except Exception as err:
            return None

    def get_location(self, obj):
        try:
            serializers = LocationSerializer(obj.location).data
            return serializers
        except Exception as err:
            return None

    def get_member(self, obj):
        try:
            serializers = MemberSerializer(obj.member, context=self.context).data
            return serializers
        except Exception as err:
            return None

    def get_client(self, obj):
        try:
            serializers = ClientSerializer(obj.client).data
            return serializers
        except Exception as err:
            return None

    class Meta:
        model = ProductOrder
        fields = ['id', 'client', 'quantity', 'status', 'created_at',
                  'location', 'member', 'tip', 'total_price', 'payment_type', 'product_price', 'price', 'name',
                  'product_name', 'gst', 'order_type', 'sold_quantity', 'product_details', 'total_product']


class ServiceOrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)

    price = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)

    def get_order_type(self, obj):
        return 'Service'

    def get_service(self, obj):
        try:
            serializers = ServiceSearchSerializer(obj.service).data
            return serializers
        except Exception as err:
            return None

    def get_location(self, obj):
        try:
            serializers = LocationSerializer(obj.location).data
            return serializers
        except Exception as err:
            return None

    def get_member(self, obj):
        try:
            serializers = MemberSerializer(obj.member, context=self.context).data
            return serializers
        except Exception as err:
            return None

    def get_client(self, obj):
        try:
            serializers = ClientSerializer(obj.client).data
            return serializers
        except Exception as err:
            return None

    def get_user(self, obj):
        try:
            return obj.user.full_name
        except Exception as err:
            return None

    def get_name(self, obj):
        try:
            return obj.service.name
        except Exception as err:
            return None

    def get_price(self, obj):
        try:
            return obj.current_price
        except Exception as err:
            return None

    class Meta:
        model = ServiceOrder
        fields = ['id', 'client', 'quantity', 'service', 'created_at', 'user',
                  'duration', 'location', 'member', 'total_price', 'name', 'price',
                  'payment_type', 'tip', 'gst', 'order_type', 'created_at'
                  ]


class SOSerializerForClientSale(serializers.ModelSerializer):
    service = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)

    def get_order_type(self, obj):
        return 'Service'

    def get_service(self, obj):
        return obj.service.name

    def get_member(self, obj):
        # return obj.member.full_name
        return obj.employee.full_name

    def get_user(self, obj):
        # return obj.user.full_name
        return obj.sale_record.user.full_name

    def get_price(self, obj):
        # return obj.current_price
        return obj.price

    class Meta:
        model = ServiceOrder
        fields = ['quantity', 'service', 'created_at', 'user',
                  'duration', 'member', 'price',
                  'payment_type', 'tip', 'gst', 'order_type', 'created_at'
                  ]


class MOrderSerializerForSale(serializers.ModelSerializer):
    member = serializers.SerializerMethodField(read_only=True)
    membership = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)

    def get_order_type(self, obj):
        return 'Membership'

    def get_member(self, obj):
        try:
            return obj.member.full_name
        except:
            return None
    def get_membership(self, obj):
        return obj.membership.name

    def get_price(self, obj):
        try:
            return obj.current_price
        except:
            return obj.price
    class Meta:
        model = MemberShipOrder
        fields = ['membership', 'order_type', 'member', 'quantity', 'price', 'created_at']


class MemberShipOrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)
    membership = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)
    membership_price = serializers.SerializerMethodField(read_only=True)

    price = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)

    def get_order_type(self, obj):
        return 'Membership'

    def get_location(self, obj):
        try:
            serializers = LocationSerializer(obj.location).data
            return serializers
        except Exception as err:
            return None

    def get_member(self, obj):
        try:
            serializers = MemberSerializer(obj.member, context=self.context).data
            return serializers
        except Exception as err:
            return None

    def get_client(self, obj):
        try:
            serializers = ClientSerializer(obj.client).data
            return serializers
        except Exception as err:
            return None

    def get_membership(self, obj):
        try:
            return obj.membership.name
        except Exception as err:
            return None

    def get_name(self, obj):
        try:
            return obj.membership.name
        except Exception as err:
            return None

    def get_membership_price(self, obj):
        try:
            return obj.current_price
        except Exception as err:
            return None

    # def get_price(self, obj):
    #     try:
    #         return obj.membership.price
    #     except Exception as err:
    #         return None

    def get_price(self, obj):
        try:
            return obj.current_price
        except Exception as err:
            return None

    # ,'location' ,'start_date', 'end_date','status', 'total_price', 'payment_type', 'order_type'

    class Meta:
        model = MemberShipOrder
        fields = ['id', 'membership', 'order_type', 'client', 'member', 'quantity'
            , 'location', 'start_date', 'end_date', 'status', 'total_price', 'name', 'price',
                  'payment_type', 'membership_price', 'created_at']


class VoucherOrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)
    voucher = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)
    voucher_price = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)

    def get_location(self, obj):
        try:
            # app_location = BusinessAddress.objects.filter(id=str(obj.location))
            return LocationSerializer(obj.location, many=True).data
        except Exception as err:
            return str(err)

    def get_order_type(self, obj):
        return 'Voucher'

    # def get_location(self, obj):

    #     try:
    #         serializers = LocationSerializer(obj.location).data
    #         return serializers
    #     except Exception as err:
    #         return None

    def get_member(self, obj):
        try:
            serializers = MemberSerializer(obj.member, context=self.context).data
            return serializers
        except Exception as err:
            return None

    def get_client(self, obj):
        try:
            serializers = ClientSerializer(obj.client).data
            return serializers
        except Exception as err:
            return None

    def get_voucher(self, obj):
        try:
            return obj.voucher.name
        except Exception as err:
            return None

    def get_name(self, obj):
        try:
            return obj.voucher.name
        except Exception as err:
            return None

    def get_voucher_price(self, obj):
        try:
            return obj.current_price
        except Exception as err:
            return None

    def get_price(self, obj):
        try:
            return obj.current_price
        except Exception as err:
            return None

    class Meta:
        model = VoucherOrder
        fields = ['id', 'voucher', 'client', 'location',
                  'member', 'start_date', 'end_date', 'status', 'quantity',
                  'total_price', 'payment_type', 'order_type', 'voucher_price', 'price', 'name', 'created_at',
                  'discount_percentage', ]


class VOSerializerForClientSale(serializers.ModelSerializer):
    # client = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)
    voucher = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)

    def get_order_type(self, obj):
        return 'Voucher'

    def get_member(self, obj):
        # return obj.member.full_name
        try:
            return obj.member.full_name
        except:
            return None

    def get_voucher(self, obj):
        try:
            return obj.voucher.name
        except:
            return None

    def get_price(self, obj):
        # return obj.current_price
        return obj.price

    class Meta:
        model = VoucherOrder
        fields = ['voucher', 'member', 'quantity', 'order_type', 'price', 'created_at', ]
        
class VoucherSerializerForClientSale(serializers.ModelSerializer):
    # client = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)
    voucher = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)

    def get_order_type(self, obj):
        return 'Voucher'

    def get_member(self, obj):
        try:
            return obj.employee.full_name
        except:
            return None

    def get_voucher(self, obj):
        try:
            return obj.voucher.name
        except:
            return None

    def get_price(self, obj):
        # return obj.current_price
        return obj.price

    class Meta:
        model = VoucherOrder
        fields = ['voucher', 'member', 'quantity', 'order_type', 'price', 'created_at', ]


class CheckoutSerializer(serializers.ModelSerializer):
    gst = serializers.FloatField(source='tax_applied')
    gst1 = serializers.FloatField(source='tax_applied1')
    gst_price = serializers.SerializerMethodField()
    gst_price1 = serializers.FloatField(source='tax_amount1')

    product = serializers.SerializerMethodField(read_only=True)  # ProductOrderSerializer(read_only = True)
    service = serializers.SerializerMethodField(read_only=True)  # serviceOrderSerializer(read_only = True)
    membership = serializers.SerializerMethodField(read_only=True)  # serviceOrderSerializer(read_only = True)
    voucher = serializers.SerializerMethodField(read_only=True)  # serviceOrderSerializer(read_only = True)

    client = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)

    ids = serializers.SerializerMethodField(read_only=True)
    membership_product = serializers.SerializerMethodField(read_only=True)
    membership_service = serializers.SerializerMethodField(read_only=True)
    membership_type = serializers.SerializerMethodField(read_only=True)

    def get_client(self, obj):
        try:
            serializers = ClientSerializer(obj.client).data
            return serializers
        except Exception as err:
            return None

    def get_member(self, obj):
        try:
            serializers = MemberSerializer(obj.member, context=self.context).data
            return serializers
        except Exception as err:
            return None

    def get_location(self, obj):
        try:
            serializers = LocationSerializer(obj.location).data
            return serializers
        except Exception as err:
            return None

    def get_membership(self, obj):
        try:
            check = MemberShipOrder.objects.filter(checkout=obj)
            # all_service = obj.product.all()
            return MemberShipOrderSerializer(check, many=True, context=self.context).data
        except Exception as err:
            print(str(err))

    def get_voucher(self, obj):
        try:
            check = VoucherOrder.objects.filter(checkout=obj)
            # all_service = obj.product.all()
            return VoucherOrderSerializer(check, many=True, context=self.context).data
        except Exception as err:
            print(str(err))

    def get_product(self, obj):
        try:
            check = ProductOrder.objects.filter(checkout=obj)
            # all_service = obj.product.all()
            return ProductOrderSerializer(check, many=True, context=self.context).data
        except Exception as err:
            print(str(err))

    def get_membership_product(self, obj):
        try:
            check = ProductOrder.objects.filter(checkout=obj)
            # all_service = obj.product.all()
            return ProductOrderSerializer(check, many=True, context=self.context).data
        except Exception as err:
            print(str(err))

    def get_service(self, obj):
        try:
            service = ServiceOrder.objects.filter(checkout=obj)
            # all_service = obj.product.all()
            return ServiceOrderSerializer(service, many=True, context=self.context).data
        except Exception as err:
            print(str(err))

    def get_membership_service(self, obj):
        try:
            service = ServiceOrder.objects.filter(checkout=obj)
            # all_service = obj.product.all()
            return ServiceOrderSerializer(service, many=True, context=self.context).data
        except Exception as err:
            print(str(err))

    def get_membership_type(self, obj):
        try:
            data = Membership.objects.filter(discount=obj).first()
            return data
        except Exception as err:
            return None

    def get_ids(self, obj):
        try:
            products = ProductOrder.objects.filter(checkout=obj)
            services = ServiceOrder.objects.filter(checkout=obj)

            product_data = ProductOrderSerializer(products, many=True, context=self.context).data
            service_data = ServiceOrderSerializer(services, many=True, context=self.context).data

            ids_data = []
            ids_data.extend(product_data)
            ids_data.extend(service_data)

            return ids_data
        except Exception as err:
            print(str(err))

    def get_gst_price(self, obj):
        try:
            return obj.tax_amount
        except:
            return 0

    class Meta:
        model = Checkout
        fields = ['id', 'product', 'service', 'membership',
                  'voucher', 'client', 'location', 'member', 'created_at', 'payment_type', 'tip',
                  'service_commission', 'voucher_commission', 'product_commission', 'service_commission_type',
                  'product_commission_type', 'voucher_commission_type', 'ids', 'membership_product',
                  'membership_service', 'membership_type',
                  'gst',
                  'gst1',
                  'gst_price',
                  'gst_price1',
                  'tax_name',
                  'tax_name1'
                  ]


class ParentBusinessTax_RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessTax
        fields = ['id', 'name', 'parent_tax', 'tax_rate', 'tax_type', 'is_active']


class ParentBusinessTaxSerializer(serializers.ModelSerializer):
    parent_tax = ParentBusinessTax_RateSerializer(many=True, read_only=True)

    class Meta:
        model = BusinessTax
        fields = ['id', 'name', 'parent_tax', 'tax_rate', 'location', 'tax_type', 'is_active']


class AppointmentCheckoutSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    voucher_discount_percentage = serializers.SerializerMethodField(read_only=True)
    appointment_service = serializers.SerializerMethodField(read_only=True)
    promotion_name = serializers.SerializerMethodField(read_only=True)

    def get_promotion_name(self, obj):
        return 'promotion name'

    def get_appointment_service(self, obj):
        service = AppointmentService.objects.filter(appointment=obj.appointment)
        return UpdateAppointmentSerializer(service, many=True).data

    def get_service(self, obj):
        try:
            cli = f"{obj.service.name}"
            return cli

        except Exception as err:
            print(err)

    def get_order_type(self, obj):
        return 'Appointment'

    def get_client(self, obj):
        try:
            serializers = ClientSerializer(obj.appointment.client).data
            return serializers
        except Exception as err:
            return None

    def get_price(self, obj):
        try:
            return obj.appointment_service.price

        except Exception as err:
            print(err)

    def get_member(self, obj):
        try:
            serializers = MemberSerializer(obj.member, context=self.context).data
            return serializers
        except Exception as err:
            return None

    def get_location(self, obj):
        try:
            serializers = LocationSerializer(obj.business_address).data
            return serializers

        except Exception as err:
            return None

    def get_voucher_discount_percentage(self, obj):
        return 'voucher discount percentage'

    class Meta:
        model = AppointmentCheckout
        fields = ['id', 'appointment', 'appointment_service', 'payment_method',
                  'service', 'member', 'business_address', 'voucher', 'promotion',
                  'membership', 'rewards', 'tip', 'gst', 'gst1', 'gst_price', 'gst_price1', 'service_price',
                  'total_price', 'service_commission', 'service_commission_type', 'voucher_discount_percentage',
                  'is_active', 'is_deleted', 'created_at', 'order_type', 'client', 'location', 'price',
                  'promotion_name',
                  'tax_name', 'tax_name1']


class AppointmentCheckout_ReportsSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)

    employee = serializers.SerializerMethodField(read_only=True)
    commission = serializers.SerializerMethodField(read_only=True)

    commission_rate = serializers.SerializerMethodField(read_only=True)
    sale = serializers.SerializerMethodField(read_only=True)

    # appointment_service  = serializers.SerializerMethodField(read_only=True)

    def get_order_type(self, obj):
        return 'Service'

    def get_commission(self, obj):
        try:
            return obj.service_commission
        except:
            return 0

    def get_commission_rate(self, obj):
        try:
            return obj.service_commission_type
        except:
            return ''

    def get_sale(self, obj):
        payment_type = 'Cash'
        tip = 0
        client = ''
        try:
            service_name = str(obj.service.name)
        except:
            service_name = ''
        try:
            price = str(obj.price)
        except:
            price = 0
        try:
            appointment_checkout = obj.appointment_service_checkout.first()
        except:
            appointment_checkout = None
            # pass
        if appointment_checkout is not None:
            tip = appointment_checkout.tip
            payment_type = appointment_checkout.payment_method
            if obj.appointment.client is not None:
                client = obj.appointment.client.full_name,
            else:
                client = ''

        return {
            'created_at': str(obj.created_at),
            'id': str(obj.id),
            'name': service_name,  # str(obj.service.name),
            'order_type': 'Service',
            'quantity': 1,
            'price': price,
            'payment_type': payment_type,  # obj.appointment_service_checkout.payment_method,
            'tip': tip,
            'client': client
        }

    def get_employee(self, obj):
        # return {
        #     'full_name' : str(obj.member.full_name),
        # }
        try:
            mem = Employee.objects.get(id=str(obj.member))
            serializers = MemberSerializer(mem, context=self.context).data
            # serializers = MemberSerializer(obj.member,context=self.context ).data
            return serializers
        except Exception as err:
            return str(err)

    def get_location(self, obj):
        try:
            serializers = LocationSerializer(obj.business_address).data
            return serializers

        except Exception as err:
            return None

    class Meta:
        model = AppointmentService
        fields = ['location', 'order_type', 'employee', 'commission', 'commission_rate', 'sale', 'created_at']


class BusinessTaxSerializer(serializers.ModelSerializer):
    parent_tax = ParentBusinessTaxSerializer(many=True, read_only=True)

    class Meta:
        model = BusinessTax
        exclude = ('created_at', 'user')


class EmployeeBusinessSerializer(serializers.ModelSerializer):
    parent_tax = ParentBusinessTaxSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        exclude = ('created_at', 'user')


class BusinessAddressSerializer(serializers.ModelSerializer):
    tax = serializers.SerializerMethodField(read_only=True)

    def get_tax(self, obj):
        try:
            tax = BusinessTax.objects.get(location=obj)
            return BusinessTaxSerializer(tax).data
        except Exception as err:
            ExceptionRecord.objects.create(
                text=f'error happen on busiens serializer line 660 {str(err)}'
            )
            print(err)

    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name', 'tax']


class OrderSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField(read_only=True)

    def get_created_at(self, obj):
        try:
            return obj.created_at
        except:
            return None

    class Meta:
        model = Order
        fields = ('__all__')


class CheckoutCommissionSerializer(serializers.ModelSerializer):
    gst = serializers.FloatField(source='tax_applied')
    gst1 = serializers.FloatField(source='tax_applied1')
    gst_price = serializers.SerializerMethodField()
    gst_price1 = serializers.FloatField(source='tax_amount1')

    employee = serializers.SerializerMethodField()
    commission = serializers.SerializerMethodField()
    commission_rate = serializers.SerializerMethodField()
    sale = serializers.SerializerMethodField()
    location = LocationSerializer()

    def get_employee(self, checkout):
        # serialized = EmployeeBusinessSerializer(checkout.member)
        # return serialized.data
        if checkout.member:
            return {
                'full_name': str(checkout.member.full_name),
            }
        return None

    def get_commission(self, checkout):
        if checkout.service_commission and checkout.service_commission > 0:
            return checkout.service_commission
        elif checkout.product_commission and checkout.product_commission > 0:
            return checkout.product_commission
        elif checkout.voucher_commission and checkout.voucher_commission > 0:
            return checkout.voucher_commission
        else:
            return 0

    def get_commission_rate(self, checkout):
        if checkout.service_commission_type:
            return checkout.service_commission_type
        elif checkout.product_commission_type:
            return checkout.product_commission_type
        elif checkout.voucher_commission_type:
            return checkout.voucher_commission_type
        else:
            return ''

    def get_sale(self, checkout):
        sale_item = {
            'errors': []
        }

        order_item = None
        name = '-------'
        price = 0
        order_type = '-------'
        payment_type = ''
        tip = ''
        client = ''

        try:
            order_item = ProductOrder.objects.get(checkout=checkout)
            name = order_item.product.name
            price = order_item.checkout.total_product_price
            payment_type = order_item.checkout.payment_type
            tip = order_item.checkout.tip
            # client = order_item.checkout.client.full_name
            if order_item.checkout.client is not None:
                client = order_item.checkout.client.full_name
            else:
                client = ''
            order_type = 'Product'
        except Exception as err:
            sale_item['errors'].append(str(err))
            try:
                order_item = ServiceOrder.objects.get(checkout=checkout)
                name = order_item.service.name
                price = order_item.checkout.total_service_price
                payment_type = order_item.checkout.payment_type
                tip = order_item.checkout.tip
                if order_item.checkout.client is not None:
                    client = order_item.checkout.client.full_name
                else:
                    client = ''
                order_type = 'Service'
            except Exception as err:
                sale_item['errors'].append(str(err))
                try:
                    order_item = VoucherOrder.objects.get(checkout=checkout)
                    name = order_item.voucher.name
                    price = order_item.checkout.total_voucher_price
                    payment_type = order_item.checkout.payment_type
                    tip = order_item.checkout.tip
                    if order_item.checkout.client is not None:
                        client = order_item.checkout.client.full_name
                    else:
                        client = ''
                    order_type = 'Voucher'

                except Exception as err:
                    sale_item['errors'].append(str(err))
                    order_item = None

        if order_item is not None:
            sale_item['quantity'] = order_item.quantity

        sale_item['name'] = name
        sale_item['price'] = price
        sale_item['order_type'] = order_type
        sale_item['payment_type'] = payment_type
        sale_item['tip'] = tip
        sale_item['client'] = client

        #         else:
        #             sale_item['voucher'] = VoucherOrderSerializer(order_item).data
        #     else:
        #         sale_item['service'] = ServiceOrderSerializer(order_item).data

        # else:
        #     sale_item['product'] = ProductOrderSerializer(order_item).data

        return {
            'created_at': str(checkout.created_at),
            'id': str(checkout.id),
            **sale_item
        }

    def get_gst_price(self, obj):
        try:
            return obj.tax_amount
        except:
            return 0

    class Meta:
        """
            'employee' : {},
            'location' : {},
            'commission' : 00,
            'commission_rate' : 00,
            'sale' : {}
        """
        model = Checkout
        fields = ['employee', 'location', 'commission', 'commission_rate', 'sale', 'created_at',
                  'gst',
                  'gst1',
                  'gst_price',
                  'gst_price1',
                  'tax_name',
                  'tax_name1'
                  ]


class PromotionNDiscount_CheckoutSerializer(serializers.ModelSerializer):
    gst = serializers.FloatField(source='tax_applied')
    gst1 = serializers.FloatField(source='tax_applied1')
    gst_price = serializers.SerializerMethodField()
    gst_price1 = serializers.FloatField(source='tax_amount1')

    promotion = serializers.SerializerMethodField(read_only=True)
    invoice = serializers.SerializerMethodField(read_only=True)
    original_price = serializers.SerializerMethodField(read_only=True)
    discounted_price = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)

    product = serializers.SerializerMethodField(read_only=True)  # ProductOrderSerializer(read_only = True)
    service = serializers.SerializerMethodField(read_only=True)  # serviceOrderSerializer(read_only = True)
    membership = serializers.SerializerMethodField(read_only=True)  # serviceOrderSerializer(read_only = True)
    voucher = serializers.SerializerMethodField(read_only=True)  # serviceOrderSerializer(read_only = True)

    client = serializers.SerializerMethodField(read_only=True)

    ids = serializers.SerializerMethodField(read_only=True)
    membership_product = serializers.SerializerMethodField(read_only=True)
    membership_service = serializers.SerializerMethodField(read_only=True)
    membership_type = serializers.SerializerMethodField(read_only=True)

    tip = serializers.SerializerMethodField(read_only=True)

    # all_products = serializers.SerializerMethodField(read_only=True)
    # all_services = serializers.SerializerMethodField(read_only=True)

    def get_client(self, obj):
        if obj.client:
            serializers = ClientSerializer(obj.client).data
            return serializers
        return None

    def get_membership(self, obj):

        check = MemberShipOrder.objects.only(
            'id',
            'membership',
            'current_price',
            'quantity',
        ).select_related(
            'membership',
        ).filter(
            checkout=obj
        )
        # return MemberShipOrderSerializer(check, many = True , context=self.context ).data
        return SaleOrder_MemberShipSerializer(check, many=True).data

    def get_voucher(self, obj):

        check = VoucherOrder.objects.only(
            'id',
            'voucher',
            'current_price',
            'quantity',
        ).select_related(
            'voucher',
        ).filter(
            checkout=obj
        )
        # return VoucherOrderSerializer(check, many = True , context=self.context ).data
        return SaleOrder_VoucherSerializer(check, many=True).data

    def get_product(self, obj):

        check = ProductOrder.objects.only(
            'current_price',
            'id',
            'quantity',
            'product',
        ).select_related(
            'product',
        ).filter(
            checkout=obj
        )
        # data =  ProductOrderSerializer(check, many = True , context=self.context ).data
        data = SaleOrder_ProductSerializer(check, many=True).data
        self.product = data
        return self.product

    def get_membership_product(self, obj):
        return self.product

    def get_service(self, obj):
        service = ServiceOrder.objects.only(
            'id',
            'quantity',
            'current_price',
            'service',
        ).select_related(
            'service',
        ).filter(
            checkout=obj
        )
        # data = ServiceOrderSerializer(service, many = True , context=self.context ).data
        data = SaleOrder_ServiceSerializer(service, many=True).data
        self.service = data
        return self.service

    def get_membership_service(self, obj):
        return self.service

    def get_membership_type(self, obj):
        data = Membership.objects.filter(discount=obj).first()
        return data

    def get_ids(self, obj):

        ids_data = []
        ids_data.extend(self.product)
        ids_data.extend(self.service)

        return ids_data

    def get_tip(self, obj):
        tips = AppointmentEmployeeTip.objects.filter(checkout=obj)
        serialized_tips = CheckoutTipsSerializer(tips, many=True).data
        return serialized_tips

    def get_invoice(self, obj):
        try:
            invoice = SaleInvoice.objects.get(checkout__icontains=obj)
            serializer = SaleInvoiceSerializer(invoice ,context=self.context)
            return serializer.data
        except Exception as e:
            return str(e)

    def get_location(self, obj):
        try:
            serializers = LocationSerializer(obj.location).data
            return serializers
        except Exception as err:
            return str(err)

    def get_promotion(self, obj):
        promotion = get_promotions(
            promotion_type=obj.selected_promotion_type,
            promotion_id=obj.selected_promotion_id
        )

        if promotion:
            return promotion

        return None

    def get_original_price(self, obj):
        checkout_orders = Order.objects.filter(
            checkout=obj
        ).annotate(
            totalPrice=F('total_price') * F('quantity')
        ).values_list('totalPrice', flat=True)
        checkout_orders = list(checkout_orders)
        checkout_orders = sum(checkout_orders)
        return checkout_orders

    def get_discounted_price(self, obj):
        chk_orders = Order.objects.filter(
            checkout=obj
        ).values_list('discount_price', flat=True)
        return sum(list(chk_orders))

    def get_gst_price(self, obj):
        try:
            return obj.tax_amount
        except:
            return 0

    class Meta:
        model = Checkout
        fields = ['id', 'gst', 'gst1', 'gst_price', 'gst_price1', 'promotion', 'invoice',
                  'created_at', 'original_price', 'discounted_price', 'location', 'product',
                  'service', 'membership', 'voucher', 'client', 'ids', 'membership_product',
                  'membership_service', 'membership_type', 'tip', 'tax_name', 'tax_name1']


class ProductSerializer_CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'cost_price', 'arabic_name']


class ServiceSerializer_CheckoutSerializer(serializers.ModelSerializer):
    price_service = serializers.SerializerMethodField(read_only=True)

    def get_price_service(self, obj):
        price = PriceService.objects.filter(service=str(obj)).order_by('-created_at')
        return PriceServiceSaleSerializer(price, many=True).data

    class Meta:
        model = Service
        fields = ['id', 'name', 'arabic_name', 'price_service']


class PriceServiceSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceService
        fields = ['id', 'service', 'duration', 'price']


class PromotionNDiscount_AppointmentCheckoutSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    promotion = serializers.SerializerMethodField(read_only=True)
    invoice = serializers.SerializerMethodField(read_only=True)
    original_price = serializers.SerializerMethodField(read_only=True)
    discounted_price = serializers.SerializerMethodField(read_only=True)

    client = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    voucher_discount_percentage = serializers.SerializerMethodField(read_only=True)
    appointment_service = serializers.SerializerMethodField(read_only=True)
    promotion_name = serializers.SerializerMethodField(read_only=True)

    tip = serializers.SerializerMethodField(read_only=True)

    def get_promotion_name(self, obj):
        return 'promotion name'

    def get_appointment_service(self, obj):
        service = AppointmentService.objects.filter(appointment=obj.appointment)
        return UpdateAppointmentSerializer(service, many=True).data

    def get_service(self, obj):
        if obj.service:
            cli = f"{obj.service.name}"
            return cli
        return None

    def get_order_type(self, obj):
        return 'Appointment'

    def get_client(self, obj):
        if obj.appointment and obj.appointment.client:
            serializers = ClientSerializer(obj.appointment.client).data
            return serializers

        return None

    def get_price(self, obj):
        if obj.appointment_service:
            return obj.appointment_service.price

        return None

    def get_voucher_discount_percentage(self, obj):
        return 'voucher discount percentage'

    def get_tip(self, obj):
        tips = AppointmentEmployeeTip.objects.filter(appointment=obj.appointment)
        serialized_tips = AppointmentTipsSerializer(tips, many=True).data
        return serialized_tips

    def get_promotion(self, obj):
        promotion = get_promotions(
            promotion_type=obj.selected_promotion_type,
            promotion_id=obj.selected_promotion_id
        )
        if promotion:
            return promotion

        return None

    def get_invoice(self, obj):
        try:
            invoice = SaleInvoice.objects.get(appointment=obj.appointment)
            serializer = SaleInvoiceSerializer(invoice, context=self.context)
            return serializer.data
        except Exception as e:
            return f" {str(e)} + {obj.appointment}"

    def get_original_price(self, obj):
        app_srevices = AppointmentService.objects.filter(
            appointment=obj.appointment,
        )
        total_price = 0

        for app_serv in app_srevices:
            if app_serv.total_price:
                total_price += app_serv.total_price
            elif app_serv.price:
                total_price += app_serv.price

        # app_srevices = list(app_srevices)
        # app_srevices = sum(app_srevices)
        return total_price

    def get_discounted_price(self, obj):
        app_srevices = AppointmentService.objects.filter(
            appointment=obj.appointment,
            discount_price__gt=0
        ).values_list('discount_price', flat=True)
        app_srevices = list(app_srevices)
        app_srevices = sum(app_srevices)
        return app_srevices

    def get_location(self, obj):
        try:
            serializers = LocationSerializer(obj.business_address).data
            return serializers
        except Exception as err:
            return None

    class Meta:
        model = AppointmentCheckout
        fields = ['id', 'promotion', 'invoice', 'created_at', 'original_price', 'discounted_price',
                  'location', 'appointment', 'client', 'order_type', 'service', 'price',
                  'voucher_discount_percentage', 'appointment_service', 'promotion_name',
                  'tip', 'gst', 'gst1', 'gst_price', 'gst_price1', 'tax_name', 'tax_name1']


class ProductTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product


class SaleOrder_ProductSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField(read_only=True)  # Method field to get the product id
    product_name = serializers.SerializerMethodField(read_only=True)
    product_arabic_name = serializers.SerializerMethodField(read_only=True)
    product_price = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    selection_type = serializers.SerializerMethodField(read_only=True)
    product_original_price = serializers.SerializerMethodField(read_only=True)
    primary_product_translation = serializers.SerializerMethodField(read_only=True)
    secondary_product_translation = serializers.SerializerMethodField(read_only=True)

    def get_primary_product_translation(self, obj):
        if obj.location.primary_translation:
            primary_invoice_traslation = InvoiceTranslation.objects.filter(
                id=obj.location.primary_translation.id).first()
            primary_product_translations = obj.product.producttranslations_set.filter(
                language__id=primary_invoice_traslation.language.id).first()
            return ProductTranlationsSerializerNew(primary_product_translations).data
        else:
            return None

    def get_secondary_product_translation(self, obj):

        if obj.location.secondary_translation:
            secondary_invoice_traslation = InvoiceTranslation.objects.filter(
                id=obj.location.secondary_translation.id).first()
            secondary_product_translations = obj.product.producttranslations_set.filter(
                language__id=secondary_invoice_traslation.language.id).first()
            return ProductTranlationsSerializerNew(secondary_product_translations).data
        else:
            return None

    # Added Field method to get the product_id By M Asad
    def get_product_id(self, obj):
        return obj.product.id

    def get_selection_type(self, obj):
        return 'PRODUCT'

    def get_product_price(self, obj):
        return obj.current_price

    def get_price(self, obj):
        if obj.is_redeemed == True:
            return obj.redeemed_price
        elif obj.discount_price:
            return obj.discount_price
        else:
            return obj.current_price

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name

        return None

    def get_product_arabic_name(self, obj):
        if obj.product:
            return obj.product.arabic_name

        return None

    def get_product_original_price(self, obj):
        price = PriceService.objects.filter(service=str(obj)).order_by('-created_at')
        return PriceServiceSaleSerializer(price, many=True).data

    class Meta:
        model = ProductOrder
        fields = [
            'id', 'product_name', 'product_arabic_name', 'product_original_price',
            'quantity', 'product_price', 'price', 'selection_type', 'discount_percentage',
            'redeemed_type', 'primary_product_translation', 'secondary_product_translation',
            'product_id']


class SaleOrder_ProductSerializerOP(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField(read_only=True)
    product_arabic_name = serializers.SerializerMethodField(read_only=True)
    product_price = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    selection_type = serializers.SerializerMethodField(read_only=True)
    product_original_price = serializers.SerializerMethodField(read_only=True)
    primary_product_translation = serializers.SerializerMethodField(read_only=True)
    secondary_product_translation = serializers.SerializerMethodField(read_only=True)

    def get_selection_type(self, obj):
        return 'PRODUCT'

    def get_product_price(self, obj):
        return obj.current_price

    def get_price(self, obj):
        if obj.is_redeemed == True:
            return obj.redeemed_price
        elif obj.discount_price:
            return obj.discount_price
        else:
            return obj.current_price

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name

        return None

    def get_product_arabic_name(self, obj):
        if obj.product:
            return obj.product.arabic_name

        return None

    def get_product_original_price(self, obj):
        price = PriceService.objects.filter(service=str(obj)).order_by('-created_at')
        return PriceServiceSaleSerializer(price, many=True).data

    class Meta:
        model = ProductOrder
        fields = [
            'id', 'product_name', 'product_arabic_name', 'product_original_price',
            'quantity', 'product_price', 'price', 'selection_type', 'discount_percentage',
            'redeemed_type', 'primary_product_translation', 'secondary_product_translation']


class SaleOrder_ServiceSerializer(serializers.ModelSerializer):
    # service_id = serializers.SerializerMethodField(read_only = True)
    service = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    selection_type = serializers.SerializerMethodField(read_only=True)
    service_original_price = serializers.SerializerMethodField(read_only=True)
    service_translations = serializers.SerializerMethodField(read_only=True)

    def get_service_translations(self, obj):
        if obj.location.secondary_translation:
            secondary_invoice_traslation = InvoiceTranslation.objects.filter(
                id=obj.location.secondary_translation.id).first()
            translations = obj.service.servicetranlations_set.filter(
                language__id=secondary_invoice_traslation.language.id)
            translations_data = ServiceTranslationsSerializer(translations, many=True).data
            return translations_data
        else:
            return None

    # def get_service_id(self, obj): # getting service id
    #     if obj.service:
    #         return obj.service.id
        
    def get_selection_type(self, obj):
        return 'SERVICE'

    def get_service(self, obj):
        if obj.service:
            return {'name': obj.service.name,
                    'arabic_name': obj.service.arabic_name,
                    'service_id':obj.service.id}
        return None

    def get_service_original_price(self, obj):
        if obj.service:
            return obj.service.price

        return None

    def get_price(self, obj):
        if obj.is_redeemed == True:
            return obj.redeemed_price
        elif obj.discount_price is not None:
            return obj.discount_price
        else:
            return obj.current_price

    class Meta:
        model = ServiceOrder
        fields = ['id', 'price', 'service_original_price', 'quantity', 'service', 'selection_type',
                  'discount_price', 'discount_percentage', 'redeemed_type', 'service_translations']


class SaleOrder_VoucherSerializer(serializers.ModelSerializer):
    voucher_price = serializers.SerializerMethodField()
    voucher = serializers.SerializerMethodField()
    voucher_arabic_name = serializers.SerializerMethodField()

    def get_voucher_price(self, obj):
        return obj.current_price

    def get_voucher(self, obj):
        return obj.voucher.name

    def get_voucher_arabic_name(self, obj):
        return obj.voucher.arabic_name

    class Meta:
        model = VoucherOrder
        fields = ['id', 'voucher', 'voucher_arabic_name', 'quantity', 'voucher_price']


class SaleOrder_MemberShipSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    membership_price = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()
    membership_arabic_name = serializers.SerializerMethodField()
    selection_type = serializers.SerializerMethodField(read_only=True)

    def get_selection_type(self, obj):
        return 'MEMBERSHIP'

    def get_price(self, obj):
        return obj.current_price

    def get_membership_price(self, obj):
        return obj.current_price

    def get_membership(self, obj):
        return obj.membership.name

    def get_membership_arabic_name(self, obj):
        return obj.membership.arabic_name

    class Meta:
        model = MemberShipOrder
        fields = ['id', 'membership', 'membership_arabic_name', 'quantity', 'price', 'membership_price',
                  'selection_type']


class CheckoutTipsSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField(read_only=True)

    def get_member_name(self, tip_obj):
        if tip_obj.member and tip_obj.member.full_name:
            return f'{tip_obj.member.full_name}'
        return ''

    class Meta:
        model = AppointmentEmployeeTip
        fields = ['id', 'member', 'tip', 'member_name']


class AppointmentTipsSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField(read_only=True)

    def get_member_name(self, tip_obj):
        if tip_obj.member and tip_obj.member.full_name:
            return f'{tip_obj.member.full_name}'
        return ''

    class Meta:
        model = AppointmentEmployeeTip
        fields = ['id', 'member', 'tip', 'member_name']



class CouponServiceGroupcouponserializersaleresponse(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"

class SaleOrders_CheckoutSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField(read_only=True)  # ProductOrderSerializer(read_only = True)
    service = serializers.SerializerMethodField(read_only=True)  # serviceOrderSerializer(read_only = True)
    membership = serializers.SerializerMethodField(read_only=True)  # serviceOrderSerializer(read_only = True)
    voucher = serializers.SerializerMethodField(read_only=True)  # serviceOrderSerializer(read_only = True)

    client = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)

    ids = serializers.SerializerMethodField(read_only=True)
    membership_product = serializers.SerializerMethodField(read_only=True)
    membership_service = serializers.SerializerMethodField(read_only=True)
    membership_type = serializers.SerializerMethodField(read_only=True)
    invoice = serializers.SerializerMethodField(read_only=True)

    gst = serializers.FloatField(source='tax_applied')
    gst1 = serializers.FloatField(source='tax_applied1')
    gst_price = serializers.FloatField(source='tax_amount')
    gst_price1 = serializers.FloatField(source='tax_amount1')

    tip = serializers.SerializerMethodField(read_only=True)
    total_tip = serializers.SerializerMethodField(read_only=True)
    client_loyalty_points = serializers.SerializerMethodField(read_only=True)
    coupon = CouponServiceGroupcouponserializersaleresponse()

    def get_client_loyalty_points(self, obj):
        return obj.get_client_loyalty_points()

    def get_client(self, obj):
        if obj.client:
            serializers = ClientSerializer(obj.client).data
            return serializers
        return None

    def get_location(self, obj):
        if obj.location:
            serializers = LocationSerializer(obj.location).data
            return serializers

        return None

    def get_membership(self, obj):

        check = MemberShipOrder.objects.only(
            'id',
            'membership',
            'current_price',
            'quantity',
        ).select_related(
            'membership',
        ).filter(
            checkout=obj
        )
        # return MemberShipOrderSerializer(check, many = True , context=self.context ).data
        return SaleOrder_MemberShipSerializer(check, many=True).data

    def get_voucher(self, obj):

        check = VoucherOrder.objects.only(
            'id',
            'voucher',
            'current_price',
            'quantity',
        ).select_related(
            'voucher',
        ).filter(
            checkout=obj
        )
        # return VoucherOrderSerializer(check, many = True , context=self.context ).data
        return SaleOrder_VoucherSerializer(check, many=True).data

    def get_product(self, obj):

        check = ProductOrder.objects.only(
            'current_price',
            'id',
            'quantity',
            'product',
        ).select_related(
            'product',
        ).filter(
            checkout=obj
        )
        # data =  ProductOrderSerializer(check, many = True , context=self.context ).data
        data = SaleOrder_ProductSerializer(check, many=True).data
        self.product = data
        return self.product

    def get_membership_product(self, obj):
        return self.product

    def get_service(self, obj):
        service = ServiceOrder.objects.only(
            'id',
            'quantity',
            'current_price',
            'service',
        ).select_related(
            'service',
        ).filter(
            checkout=obj
        )
        # data = ServiceOrderSerializer(service, many = True , context=self.context ).data
        data = SaleOrder_ServiceSerializer(service, many=True).data
        self.service = data
        return self.service

    def get_membership_service(self, obj):
        return self.service

    def get_membership_type(self, obj):
        try:
            data = Membership.objects.filter(discount=obj).first()
        except:
            pass
        return data

    def get_ids(self, obj):

        ids_data = []
        ids_data.extend(self.product)
        ids_data.extend(self.service)

        return ids_data

    def get_tip(self, obj):
        tips = AppointmentEmployeeTip.objects.filter(checkout=obj)
        serialized_tips = CheckoutTipsSerializer(tips, many=True).data
        return serialized_tips

    def get_total_tip(self, obj):
        tips = AppointmentEmployeeTip.objects.filter(checkout=obj).aggregate(
            total_tip=Sum('tip')
        )
        return tips['total_tip']

    def get_invoice(self, obj):
        try:
            invoice = SaleInvoice.objects.get(checkout__icontains=obj)
            serializer = SaleInvoiceSerializer(invoice, context=self.context)
            return serializer.data
        except Exception as e:
            return str(e)

    class Meta:
        model = Checkout
        fields = [
            'id','is_coupon_redeemed','coupon','coupon_discounted_price',
            'product', 'service', 'membership', 'voucher', 'client', 'location', 'gst', 'gst1', 'gst_price',
            'gst_price1',
            'created_at', 'payment_type', 'tip', 'service_commission', 'voucher_commission', 'product_commission',
            'service_commission_type', 'product_commission_type', 'voucher_commission_type', 'ids',
            'membership_product',
            'membership_service', 'membership_type', 'invoice', 'tax_name', 'tax_name1', 'total_discount',
            'voucher_redeem_percentage', 'redeem_option', 'total_tip', 'client_loyalty_points','is_refund'
        ]

        # Remove Member from get all sale orders


class SaleOrders_CheckoutSerializerOP(serializers.ModelSerializer):
    total_tax = serializers.FloatField()
    subtotal = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    invoice = serializers.SerializerMethodField(read_only=True)
    total_tip = serializers.SerializerMethodField(read_only=True)

    def get_client(self, obj):
        if obj.client:
            serializers = ClientSerializer(obj.client).data
            return serializers
        return None

    def get_subtotal(self, obj):
        product_total = ProductOrder.objects \
            .filter(checkout=obj) \
            .with_subtotal() \
            .aggregate(final_subtotal=Coalesce(Sum('subtotal'), 0.0))['final_subtotal']
        service_total = ServiceOrder.objects \
            .filter(checkout=obj) \
            .with_subtotal() \
            .aggregate(final_subtotal=Coalesce(Sum('subtotal'), 0.0))['final_subtotal']
        membership_total = MemberShipOrder.objects \
            .filter(checkout=obj) \
            .with_subtotal() \
            .aggregate(final_subtotal=Coalesce(Sum('subtotal'), 0.0))['final_subtotal']
        voucher_total = VoucherOrder.objects \
            .filter(checkout=obj) \
            .with_subtotal() \
            .aggregate(final_subtotal=Coalesce(Sum('subtotal'), 0.0))['final_subtotal']

        total = product_total + service_total + membership_total + voucher_total
        if obj.coupon_discounted_price:
            return total - obj.coupon_discounted_price
        else:
            return total

    def get_total_tip(self, obj):
        tips = AppointmentEmployeeTip.objects \
            .filter(checkout=obj) \
            .aggregate(
            total_tip=Coalesce(
                Sum('tip'),
                0.0,
                output_field=FloatField()
            )
        )
        return tips['total_tip']

    def get_invoice(self, obj):
        try:
            invoice = SaleInvoice.objects.get(checkout__icontains=obj) 
            serializer = SaleInvoiceSerializerOP(invoice, context=self.context)
            return serializer.data
        except Exception as e:
            return str(e)

    class Meta:
        model = Checkout
        fields = ['id', 'payment_type', 'client', 'invoice', 'created_at',
                  'subtotal', 'total_tax', 'total_tip','is_refund']


class SaleInvoiceSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField(read_only=True)

    def get_file(self, obj):
        if obj.file:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=False)
                return f'{url}{obj.file}'
            except:
                return f'{obj.file}'
        return None

    class Meta:
        model = SaleInvoice
        fields = '__all__'


class SaleInvoiceSerializerOP(serializers.ModelSerializer):
    file = serializers.SerializerMethodField(read_only=True)

    def get_file(self, obj):
        if obj.file:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=False)
                return f'{url}{obj.file}'
            except:
                return f'{obj.file}'
        return None

    class Meta:
        model = SaleInvoice
        fields = ['id', 'file','invoice_type','checkout_type'] # Added new fields checkout type and t


class Couponresponseappointment(serializers.ModelSerializer):

    class Meta:
        model = Coupon
        fields = "__all__"
class SaleOrders_AppointmentCheckoutSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    voucher_discount_percentage = serializers.SerializerMethodField(read_only=True)
    appointment_service = serializers.SerializerMethodField(read_only=True)
    promotion_name = serializers.SerializerMethodField(read_only=True)

    tip = serializers.SerializerMethodField(read_only=True)
    invoice = serializers.SerializerMethodField(read_only=True)
    total_tip = serializers.SerializerMethodField(read_only=True)

    client_loyalty_points = serializers.SerializerMethodField(read_only=True)
    coupon = Couponresponseappointment()

    def get_client_loyalty_points(self, obj):
        return obj.get_client_loyalty_points()

    def get_promotion_name(self, obj):
        return 'promotion name'

    def get_appointment_service(self, obj):
        service = AppointmentService.objects.filter(appointment=obj.appointment)
        return UpdateAppointmentSerializer(service, many=True).data

    def get_service(self, obj):
        if obj.service:
            cli = f"{obj.service.name}"
            return cli
        return None

    def get_order_type(self, obj):
        return 'Appointment'

    def get_client(self, obj):
        if obj.appointment and obj.appointment.client:
            serializers = ClientSerializer(obj.appointment.client).data
            return serializers

        return None

    def get_price(self, obj):
        if obj.appointment_service:
            return obj.appointment_service.price

        return None

    def get_location(self, obj):
        if obj.business_address:
            serializers = LocationSerializer(obj.business_address).data
            return serializers

        return None

    def get_voucher_discount_percentage(self, obj):
        return 'voucher discount percentage'

    def get_tip(self, obj):
        tips = AppointmentEmployeeTip.objects.filter(appointment=obj.appointment)
        serialized_tips = AppointmentTipsSerializer(tips, many=True).data
        return serialized_tips

    def get_total_tip(self, obj):
        tips = AppointmentEmployeeTip.objects.filter(appointment=obj.appointment).aggregate(
            total_tip=Sum('tip')
        )
        return tips['total_tip']

    def get_invoice(self, obj):
        try:
            invoice = SaleInvoice.objects.get(checkout__icontains=obj)
            serializer = SaleInvoiceSerializer(invoice,context=self.context)
            return serializer.data
        except Exception as e:
            return str(e)

    class Meta:
        model = AppointmentCheckout
        fields = ['id', 'appointment', 'is_coupon_redeemed','coupon','coupon_discounted_price','appointment_service', 'payment_method', 'service',
                  'business_address', 'voucher', 'promotion',
                  'membership', 'rewards', 'tip', 'gst', 'gst1', 'gst_price', 'gst_price1', 'service_price',
                  'total_price', 'service_commission', 'service_commission_type', 'voucher_discount_percentage',
                  'created_at', 'order_type', 'client', 'location', 'price', 'promotion_name', 'invoice',
                  'tax_name', 'tax_name1', 'total_tip', 'client_loyalty_points','is_refund']


class SaleOrders_AppointmentCheckoutSerializerOP(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)
    invoice = serializers.SerializerMethodField(read_only=True)
    total_tip = serializers.SerializerMethodField(read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    total_tax = serializers.FloatField()

    def get_order_type(self, obj):
        return 'Appointment'

    def get_client(self, obj):
        if obj.appointment and obj.appointment.client:
            serializers = ClientSerializer(obj.appointment.client).data
            return serializers

        return None

    def get_total_tip(self, obj):
        tips = AppointmentEmployeeTip.objects \
            .filter(appointment=obj.appointment) \
            .aggregate(total_tip=Coalesce(Sum('tip'), 0.0, output_field=FloatField()))
        return tips['total_tip']

    def get_invoice(self, obj):
        try:
            invoice = SaleInvoice.objects.get(checkout__icontains=obj)
            serializer = SaleInvoiceSerializerOP(invoice, context=self.context)
            return serializer.data
        except Exception as e:
            return str(e)

    # Resolved the Subtotal Error
    def get_subtotal(self, obj):
        try:
            if obj.coupon:
                total = float(obj.subtotal) - float(obj.coupon_discounted_price)
                return total
            else:
                service_subtotal=AppointmentService.objects.filter(appointment=obj.appointment).with_appointment_subtotal()\
                    .aggregate(final_subtotal=Coalesce(Sum('subtotal'), 0.0))['final_subtotal']
                return service_subtotal
        except Exception as e:
            return {'error': str(e)}
            

        #     total = obj.subtotal
        #     if obj.coupon:
        #         # return total - obj.coupon_discounted_price
        #          [obj.coupon_discounted_price, obj.coupon]
        #     else:
        #         return total
        # except:
        #     return 0

    class Meta:
        model = AppointmentCheckout
        fields = ['id', 'payment_method','order_type', 'client',
                  'invoice', 'created_at', 'subtotal', 'total_tax', 'total_tip','is_refund']
