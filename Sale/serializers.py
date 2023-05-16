from dataclasses import field
from pyexpat import model
from Appointment.serializers import UpdateAppointmentSerializer
from Business.serializers.v1_serializers import AppointmentServiceSerializer
from rest_framework import serializers
from Appointment.models import Appointment, AppointmentCheckout, AppointmentService
from Client.models import Client, Membership

from Employee.models import Employee, EmployeeProfessionalInfo, EmployeeSelectedService
from Business.models import BusinessAddress, BusinessTax
from Order.models import Checkout, MemberShipOrder, Order, ProductOrder, ServiceOrder, VoucherOrder
from Product.Constants.index import tenant_media_base_url, tenant_media_domain
from django_tenants.utils import tenant_context
from Utility.models import Currency, ExceptionRecord
from Sale.Constants.Promotion import get_promotions
from Product.models import ProductStock

from Service.models import PriceService, Service, ServiceGroup

class PriceServiceSerializers(serializers.ModelSerializer):
    currency_name = serializers.SerializerMethodField(read_only=True)
    
    def get_currency_name(self, obj):
        try:
            currency = Currency.objects.get(id  = obj.currency.id)
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
            service = Service.objects.get(id  = obj.service.id)
            return service.code
        except Exception as err:
            return str(err)
        
    def get_currency_name(self, obj):
        try:
            currency = Currency.objects.get(id  = obj.currency.id)
            return currency.code
        except Exception as err:
            return str(err)
    class Meta:
        model = PriceService
        fields = ['id','currency','service']
        
class ServiceSearchSerializer(serializers.ModelSerializer):
    priceservice = serializers.SerializerMethodField(read_only=True)
    employees = serializers.SerializerMethodField(read_only=True)
    
    def get_employees(self, obj):
        emp = EmployeeSelectedService.objects.filter(service = obj) 
        return EmployeeSelected_TenantServiceSerializer(emp, many = True, context=self.context).data
    
    def get_priceservice(self, obj):
        try:
            ser = PriceService.objects.filter(service = obj)
            return PriceServiceSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = Service
        fields = ['id','name', 'location', 'client_can_book', 'employees','priceservice', 'slot_availible_for_online']
        
class ServiceGroupSerializer(serializers.ModelSerializer):
    
    services  = serializers.SerializerMethodField(read_only=True)
    status  = serializers.SerializerMethodField(read_only=True)

    def get_status(self, obj):
        return obj.is_active
    
    def get_services(self, obj):
            all_service = obj.services.all()
            #ser = Service.objects.get(id = obj.services)
            return ServiceSearchSerializer(all_service, many = True, context=self.context).data
    
    class Meta:
        model = ServiceGroup
        fields = ['id', 'business', 'name', 'services', 'status', 'allow_client_to_select_team_member']
class ServiceGroup_TenantSerializer(serializers.ModelSerializer):
    
    services  = serializers.SerializerMethodField(read_only=True)
    status  = serializers.SerializerMethodField(read_only=True)

    def get_status(self, obj):
        return obj.is_active
    
    def get_services(self, obj):
            all_service = obj.services.all()
            #ser = Service.objects.get(id = obj.services)
            return ServiceSearchSerializer(all_service, many = True).data
    
    class Meta:
        model = ServiceGroup
        fields = ['id', 'business', 'name', 'services', 'status', 'allow_client_to_select_team_member']


class LocationSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()
    
    def get_currency(self, obj):
        return f'{obj.currency.code}'

    class Meta:
        model = BusinessAddress
        fields = ['id','address_name', 'currency']
        
class ClientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Client
        fields = ['id','full_name']
        
class MemberSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None
    class Meta:
        model = Employee
        fields = ['id','full_name', 'image' ]
        
class MemberlocationSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    
    def get_location(self, obj):
        try:
            #ser = BusinessAddress.objects.filter(id = obj.location).filter(service = obj).first()
            all_location = obj.location.filter(is_deleted=False).first()
            return LocationSerializer(all_location).data
        except Exception as err:
            return str(err)
    
    class Meta:
        model = Employee
        fields = ['id','full_name', 'location' ]
class EmployeeSelectedServiceSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    
    def get_location(self, obj):
        #def get_location(self, obj):
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
            emp = EmployeeProfessionalInfo.objects.get(employee = obj.employee.id)
            return emp.designation
        except Exception as err:
            print(err)
    
    def get_image(self, obj):
        try:
            request = self.context["request"]
            url = tenant_media_base_url(request)
            img = Employee.objects.get(id = obj.employee.id)
            return f'{url}{img.image}'
        except Exception as err:
            print(str(err))
    
    class Meta:
        model = EmployeeSelectedService
        fields = ['id', 'service', 'employee', 'level', 'full_name', 'designation','image', 'location']     

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
            emp = EmployeeProfessionalInfo.objects.get(employee = obj.employee.id)
            return emp.designation
        except Exception as err:
            print(err)
    
    def get_image(self, obj):
        try:
            tenant = self.context["tenant"]
            url = tenant_media_domain(tenant)
            img = Employee.objects.get(id = obj.employee.id)
            return f'{url}{img.image}'
        except Exception as err:
            print(str(err))
    
    class Meta:
        model = EmployeeSelectedService
        fields = ['id', 'service', 'employee', 'level', 'full_name', 'designation','image','status', 'location']
class Employee_TenantServiceSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    
    def get_location(self, obj):
        try:
            ser = BusinessAddress.objects.filter(id = obj.employee.location.id)[0]
            return LocationSerializer(ser).data
        except Exception as err:
            pass
    
    def get_full_name(self, obj):
        return obj.employee.full_name
    
    def get_designation(self, obj):
        try:
            emp = EmployeeProfessionalInfo.objects.get(employee = obj.employee.id)
            return emp.designation
        except Exception as err:
            print(err)
    
    def get_image(self, obj):
        try:
            request = self.context["request"]
            url = tenant_media_base_url(request)
            img = Employee.objects.get(id = obj.employee.id)
            return f'{url}{img.image}'
        except Exception as err:
            print(str(err))
        # try:    
        #     print(obj.employee.image)
        #     if obj.employee.image:
        #         try:
        #             print('test')
        #             request = self.context["request"]
        #             url = tenant_media_base_url(request)
        #             return f'{url}{obj.employee.image}'
        #         except Exception as err:
        #             print(err)
        #             return obj.employee.image
                    
        #     return None
        # except Exception as err:
        #     print(err)
    
    class Meta:
        model = EmployeeSelectedService
        fields = ['id', 'service', 'employee', 'level', 'full_name', 'designation','image', 'location']

class LocationServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        #fields = '__all__'
        exclude =  ['is_primary', 'is_active', 'is_closed', 'is_deleted', 'created_at', 'user', 'business', 'is_email_verified','is_mobile_verified']
        
class ServiceSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    employees = serializers.SerializerMethodField(read_only=True)
    service_group = serializers.SerializerMethodField(read_only=True)
    
    priceservice = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    
    def get_price(self, obj):
        try:
            ser = PriceService.objects.filter(service = obj).first()
            return ser.price
        except Exception as err:
            pass
            #print(err)
    
    def get_priceservice(self, obj):
        try:
            ser = PriceService.objects.filter(service = obj)
            return PriceServiceSerializers(ser, many = True).data
        except Exception as err:
            pass
            
    
    def get_service_group(self, obj):
        try:
            group = ServiceGroup.objects.filter(services = obj)
            return ServiceGroupSerializer(group, many = True ).data
        except Exception as err:
            print(str(err))
            pass
            
    
    def get_employees(self, obj):
        emp = EmployeeSelectedService.objects.filter(service = obj, employee__is_deleted = False ) 
        return EmployeeSelectedServiceSerializer(emp, many = True, context=self.context).data
        
    
    def get_location(self, obj):
        #loc = BusinessAddress.objects.filter(is_deleted = False)
        locations = obj.location.filter(is_deleted = False)
        return LocationServiceSerializer(locations, many = True, ).data
    
    #employee = EmployeeServiceSerializer(read_only=True, many = True)
    
    class Meta:
        model = Service
        fields = [
            'id',
            'name' , 
            'service_availible',
            'employees', 
            'parrent_service' , 
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
            ]
               
class ProductOrderSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    product_name  = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    product_details  = serializers.SerializerMethodField(read_only=True)
    product_price  = serializers.SerializerMethodField(read_only=True)
    
    price  = serializers.SerializerMethodField(read_only=True)
    name  = serializers.SerializerMethodField(read_only=True)
    total_product  = serializers.SerializerMethodField(read_only=True)
    
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

    #item_sold = serializers.SerializerMethodField(read_only=True)
    
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
        fields = ['id', 'client','quantity','status','created_at',
                  'location', 'member', 'tip', 'total_price' , 'payment_type','product_price','price','name',
                  'product_name', 'gst', 'order_type', 'sold_quantity','product_details','total_product' ]
          
class ServiceOrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    user  = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    
    price  = serializers.SerializerMethodField(read_only=True)
    name  = serializers.SerializerMethodField(read_only=True)
    
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
        fields = ['id', 'client','quantity', 'service','created_at' ,'user',
                  'duration', 'location', 'member', 'total_price','name','price',
                  'payment_type','tip','gst', 'order_type','created_at'
                  ]
        
class MemberShipOrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    membership  = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    membership_price  = serializers.SerializerMethodField(read_only=True)
    
    price  = serializers.SerializerMethodField(read_only=True)
    name  = serializers.SerializerMethodField(read_only=True)
    
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
            serializers = MemberSerializer(obj.member, context=self.context ).data
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
        fields =['id', 'membership','order_type' ,'client','member','quantity'
                 ,'location' ,'start_date', 'end_date','status', 'total_price', 'name','price',
                 'payment_type','membership_price', 'created_at' ]
        
class VoucherOrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    voucher = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    voucher_price  = serializers.SerializerMethodField(read_only=True)
    price  = serializers.SerializerMethodField(read_only=True)
    name  = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        try:
            # app_location = BusinessAddress.objects.filter(id=str(obj.location))
            return LocationSerializer(obj.location, many = True).data
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
        fields =['id', 'voucher', 'client' , 'location' , 
                 'member' ,'start_date', 'end_date','status','quantity',
                 'total_price', 'payment_type' , 'order_type','voucher_price','price', 'name','created_at','discount_percentage', ]
    

        
class CheckoutSerializer(serializers.ModelSerializer):
    product  = serializers.SerializerMethodField(read_only=True) #ProductOrderSerializer(read_only = True)
    service  = serializers.SerializerMethodField(read_only=True) #serviceOrderSerializer(read_only = True)
    membership  = serializers.SerializerMethodField(read_only=True) #serviceOrderSerializer(read_only = True)
    voucher  = serializers.SerializerMethodField(read_only=True) #serviceOrderSerializer(read_only = True)
    
    client = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
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
            serializers = MemberSerializer(obj.member,context=self.context ).data
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
            check = MemberShipOrder.objects.filter(checkout =  obj)
            #all_service = obj.product.all()
            return MemberShipOrderSerializer(check, many = True , context=self.context ).data
        except Exception as err:
            print(str(err))


    def get_voucher(self, obj):
        try:
            check = VoucherOrder.objects.filter(checkout =  obj)
            #all_service = obj.product.all()
            return VoucherOrderSerializer(check, many = True , context=self.context ).data
        except Exception as err:
            print(str(err))


    def get_product(self, obj):
        try:
            check = ProductOrder.objects.filter(checkout =  obj)
            #all_service = obj.product.all()
            return ProductOrderSerializer(check, many = True , context=self.context ).data
        except Exception as err:
            print(str(err))
            
    def get_membership_product(self, obj):
        try:
            check = ProductOrder.objects.filter(checkout =  obj)
            #all_service = obj.product.all()
            return ProductOrderSerializer(check, many = True , context=self.context ).data
        except Exception as err:
            print(str(err))

    def get_service(self, obj):
        try:
            service = ServiceOrder.objects.filter(checkout =  obj)
            #all_service = obj.product.all()
            return ServiceOrderSerializer(service, many = True , context=self.context ).data
        except Exception as err:
            print(str(err))
    
    def get_membership_service(self, obj):
        try:
            service = ServiceOrder.objects.filter(checkout =  obj)
            #all_service = obj.product.all()
            return ServiceOrderSerializer(service, many = True , context=self.context ).data
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
    
    
    class Meta:
        model = Checkout
        fields = ['id', 'product', 'service', 'membership',
                  'voucher','client','location','member','created_at','payment_type', 'tip',
                  'service_commission', 'voucher_commission', 'product_commission', 'service_commission_type',
                  'product_commission_type','voucher_commission_type','ids','membership_product',
                  'membership_service','membership_type'
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
    order_type  = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    service  = serializers.SerializerMethodField(read_only=True)
    price  = serializers.SerializerMethodField(read_only=True)
    voucher_discount_percentage = serializers.SerializerMethodField(read_only=True)
    appointment_service  = serializers.SerializerMethodField(read_only=True)
    promotion_name  = serializers.SerializerMethodField(read_only=True)
    
    def get_promotion_name(self, obj):
        return 'promotion name'

    def get_appointment_service(self, obj):
        service = AppointmentService.objects.filter(appointment = obj.appointment)
        return UpdateAppointmentSerializer(service, many = True).data
    
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
            serializers = MemberSerializer(obj.member,context=self.context ).data
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
        fields = ['id','appointment','appointment_service','payment_method',
                 'service','member','business_address','voucher','promotion',
                 'membership','rewards','tip','gst','gst_price','service_price',
                 'total_price','service_commission','service_commission_type','voucher_discount_percentage',
                 'is_active','is_deleted','created_at', 'order_type', 'client', 'location', 'price', 'promotion_name']
        
class AppointmentCheckout_ReportsSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    
    employee  = serializers.SerializerMethodField(read_only=True)
    commission  = serializers.SerializerMethodField(read_only=True)
    
    commission_rate  = serializers.SerializerMethodField(read_only=True)
    sale =serializers.SerializerMethodField(read_only=True)
    
    #appointment_service  = serializers.SerializerMethodField(read_only=True)
            
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
            service_name = str(obj.service.name )
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
            #pass
        if appointment_checkout is not None:
            tip = appointment_checkout.tip
            payment_type = appointment_checkout.payment_method
            if obj.appointment.client is not None:
                client =  obj.appointment.client.full_name,
            else:
                client = ''
        
        return {
            'created_at' : str(obj.created_at),
            'id' : str(obj.id),
            'name' : service_name, #str(obj.service.name),
            'order_type' : 'Service',
            'quantity' : 1,
            'price' : price,
            'payment_type' : payment_type, #obj.appointment_service_checkout.payment_method,
            'tip' : tip,  
            'client': client
        }
        
            
    def get_employee(self, obj):
        # return {
        #     'full_name' : str(obj.member.full_name),
        # }
        try:
            mem = Employee.objects.get(id = str(obj.member))
            serializers = MemberSerializer(mem , context=self.context ).data
            #serializers = MemberSerializer(obj.member,context=self.context ).data
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
        fields = ['location','order_type','employee','commission','commission_rate','sale', 'created_at']

class BusinessTaxSerializer(serializers.ModelSerializer):
    parent_tax = ParentBusinessTaxSerializer(many=True, read_only=True)
    
    class Meta:
        model = BusinessTax
        exclude = ('created_at','user')
class EmployeeBusinessSerializer(serializers.ModelSerializer):
    parent_tax = ParentBusinessTaxSerializer(many=True, read_only=True)
    
    class Meta:
        model = Employee
        exclude = ('created_at','user')
    
class BusinessAddressSerializer(serializers.ModelSerializer):
    tax = serializers.SerializerMethodField(read_only=True)
    
    
    def get_tax(self, obj):
        try:
            tax = BusinessTax.objects.get(location = obj)
            return BusinessTaxSerializer(tax).data
        except Exception as err:
            ExceptionRecord.objects.create(
                text = f'error happen on busiens serializer line 660 {str(err)}'
            )
            print(err)
            
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name','tax']
        
class OrderSerializer(serializers.ModelSerializer):
    
    created_at = serializers.SerializerMethodField(read_only=True)
    
    def get_created_at(self, obj):
        try:
            return obj.created_at
        except:
            return None
    class Meta:
        model =  Order
        fields = ('__all__')


class CheckoutCommissionSerializer(serializers.ModelSerializer):

    employee = serializers.SerializerMethodField()
    commission = serializers.SerializerMethodField()
    commission_rate = serializers.SerializerMethodField()
    sale = serializers.SerializerMethodField()
    location = LocationSerializer()
    

    def get_employee(self, checkout):
        # serialized = EmployeeBusinessSerializer(checkout.member)
        # return serialized.data
        return {
            'full_name' : str(checkout.member.full_name),
        }

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
            'errors' : []
        }

        order_item = None
        name = '-------'
        price = 0
        order_type = '-------'
        payment_type = ''
        tip = ''
        client = ''


        try:
            order_item = ProductOrder.objects.get(checkout = checkout)
            name = order_item.product.name
            price = order_item.checkout.total_product_price
            payment_type = order_item.checkout.payment_type
            tip = order_item.checkout.tip
            #client = order_item.checkout.client.full_name
            if order_item.checkout.client is not None:
                client = order_item.checkout.client.full_name
            else:
                client = ''
            order_type = 'Product'
        except Exception as err:
            sale_item['errors'].append(str(err))
            try:
                order_item = ServiceOrder.objects.get(checkout = checkout)
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
                    order_item = VoucherOrder.objects.get(checkout = checkout)
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
            'created_at' : str(checkout.created_at),
            'id' : str(checkout.id),
            **sale_item
        }

    class Meta:
        """
            'employee' : {},
            'location' : {},
            'commission' : 00,
            'commission_rate' : 00,
            'sale' : {}
        """
        model = Checkout
        fields = ['employee', 'location', 'commission', 'commission_rate', 'sale', 'created_at']
    
    

class PromotionNDiscount_CheckoutSerializer(serializers.ModelSerializer):
    promotion = serializers.SerializerMethodField(read_only=True)
    invoice = serializers.SerializerMethodField(read_only=True)
    original_price = serializers.SerializerMethodField(read_only=True)
    discounted_price = serializers.SerializerMethodField(read_only=True)
    
    def get_promotion(self, obj):
        promotion = get_promotions(
            promotion_type=obj.selected_promotion_type,
            promotion_id=obj.selected_promotion_id
        )
        
        if promotion:
            return promotion

        return None
        
    def get_invoice(self, obj):
        return {}
        
    def get_original_price(self, obj):
        return 999
    

    def get_discounted_price(self, obj):
        return 999
        
    class Meta:
        model = Checkout
        fields = ['id', 'promotion', 'invoice', 'created_at', 'original_price', 'discounted_price', 'location']

class PromotionNDiscount_AppointmentCheckoutSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    promotion = serializers.SerializerMethodField(read_only=True)
    invoice = serializers.SerializerMethodField(read_only=True)
    original_price = serializers.SerializerMethodField(read_only=True)
    discounted_price = serializers.SerializerMethodField(read_only=True)
    
    def get_promotion(self, obj):
        promotion = get_promotions(
            promotion_type=obj.selected_promotion_type,
            promotion_id=obj.selected_promotion_id
        )
        if promotion:
            return promotion

        return None
        
    def get_invoice(self, obj):
        return {}
        
    def get_original_price(self, obj):
        return 999
    

    def get_discounted_price(self, obj):
        return 999
    
        
    def get_location(self, obj):
        try:
            serializers = LocationSerializer(obj.business_address).data
            return serializers
        except Exception as err:
            return None
        
    class Meta:
        model = AppointmentCheckout
        fields = ['id', 'promotion', 'invoice', 'created_at', 'original_price', 'discounted_price', 'location']



class SaleOrder_ProductSerializer(serializers.ModelSerializer):
    product_name  = serializers.SerializerMethodField(read_only=True)
    product_price  = serializers.SerializerMethodField(read_only=True)
    price  = serializers.SerializerMethodField(read_only=True)
    selection_type  = serializers.SerializerMethodField(read_only=True)

    def get_selection_type(self, obj):
        return 'PRODUCT'


    def get_product_price(self, obj):
        return obj.current_price
    
    def get_price(self, obj):
        return obj.current_price
        

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        
        return None


    class Meta:
        model = ProductOrder
        fields = [
            'id', 'product_name', 'quantity', 'product_price', 'price']
            # 'client','status', 'created_at',
            #       'location', 'member', 'tip', 'total_price' , 'payment_type','price','name',
            #       'gst', 'order_type', 'sold_quantity','product_details','total_product'

class SaleOrder_ServiceSerializer(serializers.ModelSerializer):

    service = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    selection_type  = serializers.SerializerMethodField(read_only=True)

    def get_selection_type(self, obj):
        return 'SERVICE'
    

    def get_service(self, obj):
        if obj.service:
            return {'name' : obj.service.name}
        return None
    
    def get_price(self, obj):
        return obj.current_price

    class Meta:
        model = ServiceOrder
        fields = ['id', 'price', 'quantity', 'service' ]
            # 'client','created_at' ,'user',
            #       'duration', 'location', 'member', 'total_price',
            #       'payment_type','tip','gst', 'order_type','created_at'

class SaleOrder_VoucherSerializer(serializers.ModelSerializer):
    voucher_price = serializers.SerializerMethodField()
    voucher = serializers.SerializerMethodField()

    def get_voucher_price(self, obj):
        return obj.current_price

    def get_voucher(self, obj):
            return obj.voucher.name
            
    class Meta:
        model = VoucherOrder
        fields =[ 'id', 'voucher', 'quantity', 'voucher_price' ]
            # 'client', 'location' , 
            #      'member' ,'start_date', 'end_date','status',
            #      'total_price', 'payment_type' , 'order_type','price', 'name','created_at','discount_percentage'
    

class SaleOrder_MemberShipSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    membership_price = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()
    selection_type  = serializers.SerializerMethodField(read_only=True)

    def get_selection_type(self, obj):
        return 'MEMBERSHIP'

    def get_price(self, obj):
        return obj.current_price
    
    def get_membership_price(self, obj):
        return obj.current_price

    def get_membership(self, obj):
        return obj.membership.name
        
    class Meta:
        model = MemberShipOrder
        fields =['id', 'membership', 'quantity', 'price', 'membership_price' ]
            # 'order_type' ,'client','member', 'location' ,'start_date', 'end_date','status', 'total_price', 'name',
            #      'payment_type','created_at'


class SaleOrders_CheckoutSerializer(serializers.ModelSerializer):
    product  = serializers.SerializerMethodField(read_only=True) #ProductOrderSerializer(read_only = True)
    service  = serializers.SerializerMethodField(read_only=True) #serviceOrderSerializer(read_only = True)
    membership  = serializers.SerializerMethodField(read_only=True) #serviceOrderSerializer(read_only = True)
    voucher  = serializers.SerializerMethodField(read_only=True) #serviceOrderSerializer(read_only = True)
    
    client = serializers.SerializerMethodField(read_only=True)
    # member  = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)

    ids = serializers.SerializerMethodField(read_only=True)
    membership_product = serializers.SerializerMethodField(read_only=True)
    membership_service = serializers.SerializerMethodField(read_only=True)
    membership_type = serializers.SerializerMethodField(read_only=True)
    
        
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
            checkout = obj
        )
        # return MemberShipOrderSerializer(check, many = True , context=self.context ).data
        return SaleOrder_MemberShipSerializer(check, many = True ).data


    def get_voucher(self, obj):
        
        check = VoucherOrder.objects.only(
            'id',
            'voucher',
            'current_price',
            'quantity',
        ).select_related(
            'voucher',
        ).filter(
            checkout = obj
        )
        # return VoucherOrderSerializer(check, many = True , context=self.context ).data
        return SaleOrder_VoucherSerializer(check, many = True ).data


    def get_product(self, obj):
        
        check = ProductOrder.objects.only(
                'current_price', 
                'id',
                'quantity',
                'product',
            ).select_related(
                'product',
            ).filter(
            checkout = obj
        )
        # data =  ProductOrderSerializer(check, many = True , context=self.context ).data
        data =  SaleOrder_ProductSerializer(check, many = True ).data
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
            checkout = obj
        )
        # data = ServiceOrderSerializer(service, many = True , context=self.context ).data
        data = SaleOrder_ServiceSerializer(service, many = True ).data
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
    
    
    class Meta:
        model = Checkout
        fields = [
            'id', 
            'product', 'service', 'membership', 'voucher',
            'client', 'location', 
            # 'member', 
            'created_at', 'payment_type', 'tip',
            'service_commission', 'voucher_commission', 'product_commission', 'service_commission_type',
            'product_commission_type', 'voucher_commission_type', 'ids', 'membership_product',
            'membership_service', 'membership_type'
        ]

        # Remove Member from get all sale orders


class SaleOrders_AppointmentCheckoutSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    service  = serializers.SerializerMethodField(read_only=True)
    price  = serializers.SerializerMethodField(read_only=True)
    voucher_discount_percentage = serializers.SerializerMethodField(read_only=True)
    appointment_service  = serializers.SerializerMethodField(read_only=True)
    promotion_name  = serializers.SerializerMethodField(read_only=True)
    
    def get_promotion_name(self, obj):
        return 'promotion name'

    def get_appointment_service(self, obj):
        service = AppointmentService.objects.filter(appointment = obj.appointment)
        return UpdateAppointmentSerializer(service, many = True).data
    
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
    class Meta:
        model = AppointmentCheckout
        fields = ['id', 'appointment', 'appointment_service', 'payment_method', 'service',
                 'business_address', 'voucher', 'promotion',
                 'membership', 'rewards', 'tip', 'gst', 'gst_price', 'service_price',
                 'total_price', 'service_commission', 'service_commission_type', 'voucher_discount_percentage',
                 'created_at', 'order_type', 'client', 'location', 'price', 'promotion_name']
        