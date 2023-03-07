from datetime import date, datetime
from Product.models import Brand
from Utility.models import ExceptionRecord
from rest_framework import serializers
from Appointment.models import AppointmentCheckout, AppointmentService
from Appointment.serializers import LocationSerializer
from Business.models import BusinessAddress
from Employee.models import Employee
from Product.Constants.index import tenant_media_base_url

from Order.models import MemberShipOrder, ProductOrder, ServiceOrder, VoucherOrder
from Sale.serializers import ProductOrderSerializer
from Service.models import Service, ServiceGroup
from TragetControl.models import RetailTarget, ServiceTarget, StaffTarget, StoreTarget, TierStoreTarget
from TragetControl.serializers import RetailTargetSerializers, StaffTargetSerializers, StoreTargetSerializers, TierStoreTargetSerializers
from Utility.Constants.Data.months import MONTH_DICT


class ServiceOrderSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)

    def get_location(self, obj):
        loc = BusinessAddress.objects.get(id  = str(obj.checkout.location))
        return LocationSerializer(loc ).data
    class Meta:
        model = ServiceOrder
        fields = ('total_price', 'sold_quantity','current_price', 'location','created_at')
        
class AppointmentCheckoutReportSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)

    def get_location(self, obj):
        loc = BusinessAddress.objects.get(id  = str(obj.business_address))
        return LocationSerializer(loc ).data
    class Meta:
        model = AppointmentCheckout
        fields = ['total_price', 'created_at', 'location']

class ServiceReportSerializer(serializers.ModelSerializer):
    sale = serializers.SerializerMethodField(read_only=True)
    #location = serializers.SerializerMethodField(read_only=True)
    
    
    # def get_location(self, obj):
    #     loc = obj.location.all()
    #     return LocationSerializer(loc, many =True ).data
    
    def get_sale(self, obj):
        data = []
        try:
            service_orders = ServiceOrder.objects.filter(
                            is_deleted=False,
                            service = obj,
                            #created_at__icontains = year
                            )
            serialized = ServiceOrderSerializer(service_orders, many = True)
            data.extend(serialized.data)
            
            
            appointment_checkout = AppointmentCheckout.objects.filter(appointment_service__appointment_status = 'Done')
            serialized = AppointmentCheckoutReportSerializer(appointment_checkout, many = True)
            data.extend(serialized.data)
            
            return data
        except Exception as err:
            return str(err)
    
    class Meta:
        model = Service
        fields = ['id','name', 'sale']

class ReportsEmployeSerializer(serializers.ModelSerializer):    
    image = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField(read_only=True)
    
    service_sale_price = serializers.SerializerMethodField(read_only=True)
    product_sale_price = serializers.SerializerMethodField(read_only=True)
    
    staff_target = serializers.SerializerMethodField(read_only=True)
        
    def get_product_sale_price(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            total = 0
            
            service_orders = ProductOrder.objects.filter(
                is_deleted=False, 
                member = obj, 
                created_at__icontains = year
                )
            for ord  in service_orders:
                create = str(ord.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if int(month) == match:
                    total += int(ord.total_price)
            
            return f'{total}'
                
        except Exception as err:
            return str(err)
    
    def get_service_sale_price(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            total = 0
            app   = AppointmentService.objects.filter(
                member = obj,
                appointment_status = 'Done',
                created_at__icontains = year
            )
        
            service_orders = ServiceOrder.objects.filter(is_deleted=False, 
                        member = obj,
                        created_at__icontains = year
                        )
            for appointment in app:
                create = str(appointment.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if int(month) == match:
                    total += int(appointment.price)
                    
            for ord  in service_orders:
                create = str(ord.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if int(month) == match:
                    total += int(ord.total_price)
                                
            return f'{total}'         
            
        except Exception as err:
            return str(err)
        
    def get_staff_target(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            service_target = 0
            retail_target = 0
            data = {}
            
            staff_target = StaffTarget.objects.filter(
                employee = obj,
                 created_at__icontains = year                
                ) 
            for ord  in staff_target:
                create = str(ord.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                ExceptionRecord.objects.create(
                text = f'months {match}{ int(month) == match }'
            )
                if int(month) == match:
                    service_target += int(ord.service_target)
                    retail_target += int(ord.retail_target)
            data.update({
                'service_target': service_target,
                'retail_target': retail_target
            })
            
            return data
            
        except Exception as err:
            return str(err)
            
    
    def get_location(self, obj):
        loc = obj.location.all()
        return LocationSerializer(loc, many =True ).data
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    class Meta:
        model = Employee
        fields = ['id', 'employee_id','is_active','full_name','image','location',
                  'created_at','staff_target', 'product_sale_price','service_sale_price']

class ComissionReportsEmployeSerializer(serializers.ModelSerializer):    
    image = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField(read_only=True)
    
    service_sale_price = serializers.SerializerMethodField(read_only=True)
    product_sale_price = serializers.SerializerMethodField(read_only=True)
    voucher_sale_price = serializers.SerializerMethodField(read_only=True)
            
    def get_product_sale_price(self, obj):
        try:

            range_start = self.context["range_start"]
            range_end = self.context["range_end"]
            year = self.context["year"] 
            
            if range_start:
                range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
                range_end = datetime.strptime(range_end, "%Y-%m-%d").date()
                                          
            total = 0
            service_commission = 0
            
            product_commission = 0
            voucher_commission = 0
            data = {}
            app   = AppointmentService.objects.filter(
                member = obj,
                appointment_status = 'Done',
                #created_at__icontains = year
            )
            for appointment  in app:                
                create = str(appointment.created_at)
                created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
                
                if range_start:
                    if range_start >= created_at  and created_at <= range_end:
                        service_commission += int(appointment.service_commission)
                else:
                    service_commission += int(appointment.service_commission)
                    
            ExceptionRecord.objects.create(
                    text=str(service_commission)
                )
            
            service_orders = ProductOrder.objects.filter(
                is_deleted=False, 
                member = obj, 
                )
            for ord  in service_orders:
                create = str(ord.created_at)
                created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
                if range_start is not None:
                    if created_at >= range_start  and created_at <= range_end:
                        total += int(ord.checkout.total_service_price)
                        service_commission += ord.checkout.service_commission
                        product_commission += ord.checkout.product_commission
                        voucher_commission += ord.checkout.voucher_commission
        
                else:
                    total += int(ord.checkout.total_product_price)
                    service_commission += ord.checkout.service_commission
                    product_commission += ord.checkout.product_commission
                    voucher_commission += ord.checkout.voucher_commission

            commission_total = service_commission + product_commission + voucher_commission
            data.update({
                'product_sale_price': total,
                'commission_total': commission_total,
                'service_commission': service_commission,
                'product_commission': product_commission,
                'voucher_commission': voucher_commission,
            })
            return data
                
        except Exception as err:
            return str(err)
    
    def get_service_sale_price(self, obj):
        try:
            range_start = self.context["range_start"]
            range_end = self.context["range_end"]
            year = self.context["year"]
            
            if range_start:
                range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
                range_end = datetime.strptime(range_end, "%Y-%m-%d").date()
            
            total = 0
            service_orders = ServiceOrder.objects.filter(is_deleted=False, 
                        member = obj,
                        #created_at__icontains = year
                        )
            app   = AppointmentService.objects.filter(
                member = obj,
                appointment_status = 'Done',
                #created_at__icontains = year
            )
            for appointment  in app:                
                create = str(appointment.created_at)
                created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
                
                if range_start:
                    if range_start >= created_at  and created_at <= range_end:
                        total += int(appointment.price)
                else:
                    total += int(appointment.price)
                    
            for ord  in service_orders:                
                create = str(ord.created_at)
                created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
                
                if range_start:
                    if range_start >= created_at  and created_at <= range_end:
                        total += int(ord.checkout.total_service_price)
                else:
                    total += int(ord.checkout.total_service_price)
                                          
            return total         
            
        except Exception as err:
            return str(err)
        
    def get_voucher_sale_price(self, obj):
        try:
            range_start = self.context["range_start"]
            range_end = self.context["range_end"]            
            year = self.context["year"]
            
            if range_start:
                range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
                range_end = datetime.strptime(range_end, "%Y-%m-%d").date()
            
            total = 0
            service_orders = VoucherOrder.objects.filter(is_deleted=False, 
                        member = obj,
                        #created_at__icontains = year
                        )
            for ord  in service_orders:
                create = str(ord.created_at)
                created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
                
                if range_start:
                    if range_start >= created_at  and created_at <= range_end:
                        total += int(ord.checkout.total_voucher_price)
                else:
                    total += int(ord.checkout.total_voucher_price)
                                
            return total         
            
        except Exception as err:
            return str(err)         
    
    def get_location(self, obj):
        loc = obj.location.all()
        return LocationSerializer(loc, many =True ).data
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_id','is_active','full_name','image','location',
                  'created_at','product_sale_price','service_sale_price', 'voucher_sale_price']
        
class BusinesAddressReportSerializer(serializers.ModelSerializer): 
    
    service_sale_price = serializers.SerializerMethodField(read_only=True)    
    product_sale_price = serializers.SerializerMethodField(read_only=True)
    voucher_sale_price = serializers.SerializerMethodField(read_only=True)
    membership_sale_price = serializers.SerializerMethodField(read_only=True)
    
    tier_target = serializers.SerializerMethodField(read_only=True)
    
    def get_tier_target(self,obj):
        try:
            tier = StoreTarget.objects.filter(
                )
                
            return StoreTargetSerializers(tier,many = True ,context=self.context).data
        except Exception as err:
            return str(err)
    
    def get_service_sale_price(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            total = 0
            
            app   = AppointmentService.objects.filter(
                business_address = obj,
                appointment_status = 'Done',
            )
            service_orders = ServiceOrder.objects.filter(is_deleted=False,
                        location = obj,
                        created_at__icontains = year
                        )
            
            for ord  in app:
                create = str(ord.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if int(month) == match:
                    total += int(ord.price)
            
            for ord  in service_orders:
                create = str(ord.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if int(month) == match:
                    total += int(ord.checkout.total_service_price)
                                
            return total         
            
        except Exception as err:
            return str(err)
    
    def get_product_sale_price(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            total = 0

            service_orders = ProductOrder.objects.filter(
                is_deleted=False, 
                location = obj,
                created_at__icontains = year
                )
            for ord  in service_orders:
                create = str(ord.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if int(month) == match:
                    total += int(ord.checkout.total_product_price)
            
            return total
                
        except Exception as err:
            return str(err)
        
    def get_voucher_sale_price(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            total = 0

            service_orders = VoucherOrder.objects.filter(
                is_deleted=False, 
                location = obj,
                created_at__icontains = year,
                )
            for ord  in service_orders:
                create = str(ord.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if int(month) == match:
                    total += int(ord.checkout.total_voucher_price)
            
            return total
                
        except Exception as err:
            return str(err)
    
    def get_membership_sale_price(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            total = 0

            service_orders = MemberShipOrder.objects.filter(
                is_deleted=False, 
                location = obj,
                created_at__icontains = year,
                )
            for ord  in service_orders:
                create = str(ord.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if int(month) == match:
                    total += int(ord.checkout.total_membership_price)
            
            return total
                
        except Exception as err:
            return str(err)
    
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name','voucher_sale_price','membership_sale_price',
                  'service_sale_price', 'product_sale_price', 'tier_target','created_at',
                  ]
    
class StaffCommissionReport(serializers.ModelSerializer):
    service_sale_price = serializers.SerializerMethodField(read_only=True)
    product_sale_price = serializers.SerializerMethodField(read_only=True)
    voucher_sale_price = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField(read_only=True)
    
    def get_service_sale_price(self, obj):
        try:
            range_start = self.context["range_start"]
            range_end = self.context["range_end"]
            year = self.context["year"]
            
            if range_start:
                range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
                range_end = datetime.strptime(range_end, "%Y-%m-%d").date()
            
            data = {}
            service_orders = ServiceOrder.objects.filter(is_deleted=False, 
                        member = obj,
                        #created_at__icontains = year
                        )
            for ord  in service_orders:                
                create = str(ord.created_at)
                created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
                
                if range_start:
                    if range_start >= created_at  and created_at <= range_end:
                        rate = ord.checkout.service_commission_type
                        #total += int(ord.total_price)
                        #sale_value = ord.sold_quantity * 
                        data.update({
                            'id': ord.id,
                            'item_sold': ord.service.name,
                            'ItemType': 'Service',
                            'Quantity': ord.quantity,
                            'Sale_Value': ord.checkout.total_service_price,
                            'Commission_amount': ord.checkout.service_commission,
                            'Commission_Rate': rate if rate != "null" else 0  ,
                            'cerated_at': ord.created_at
                        })
                else:
                    rate = ord.checkout.service_commission_type
                    data.update({
                            'id': ord.id,
                            'item_sold': ord.service.name,
                            'ItemType': 'Service',
                            'Quantity': ord.quantity,
                            'Sale_Value': ord.checkout.total_service_price,
                            'Commission_amount': ord.checkout.service_commission,
                            'Commission_Rate': rate if rate != "null"  else 0  ,
                            'cerated_at': ord.created_at
                        })
                                
            return data         
            
        except Exception as err:
            return str(err)
        
    def get_product_sale_price(self, obj):
        try:
            range_start = self.context["range_start"]
            range_end = self.context["range_end"]
            year = self.context["year"]
            
            if range_start:
                range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
                range_end = datetime.strptime(range_end, "%Y-%m-%d").date()
            
            data = {}
            service_orders = ProductOrder.objects.filter(is_deleted=False, 
                        member = obj,
                        #created_at__icontains = year
                        )
            for ord  in service_orders:                
                create = str(ord.created_at)
                created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
                
                if range_start:
                    if range_start >= created_at  and created_at <= range_end:
                        rate = ord.checkout.product_commission_type
                        #total += int(ord.total_price)
                        #sale_value = ord.sold_quantity * 
                        data.update({
                            'id': ord.id,
                            'item_sold': ord.product.name,
                            'ItemType': 'Product',
                            'Quantity': ord.quantity,
                            'Sale_Value': ord.total_price,
                            'Commission_amount': ord.checkout.product_commission,
                            'Commission_Rate': rate if rate != None else 0  ,
                            'cerated_at': ord.created_at
                        })
                else:
                    rate = ord.checkout.product_commission_type
                    data.update({
                            'id': ord.id,
                            'item_sold': ord.product.name,
                            'ItemType': 'Product',
                            'Quantity': ord.quantity,
                            'Sale_Value': ord.total_price,
                            'Commission_amount': ord.checkout.product_commission,
                            'Commission_Rate': rate if rate != None else 0  ,
                            'cerated_at': ord.created_at
                        })
                                
            return data         
            
        except Exception as err:
            return str(err)
    
    def get_voucher_sale_price(self, obj):
        try:
            range_start = self.context["range_start"]
            range_end = self.context["range_end"]
            year = self.context["year"]
            
            if range_start:
                range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
                range_end = datetime.strptime(range_end, "%Y-%m-%d").date()
            
            data = {}
            service_orders = VoucherOrder.objects.filter(is_deleted=False, 
                        member = obj,
                        #created_at__icontains = year
                        )
            for ord  in service_orders:                
                create = str(ord.created_at)
                created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
                
                if range_start:
                    if range_start >= created_at  and created_at <= range_end:
                        rate = ord.checkout.voucher_commission_type
                        #total += int(ord.total_price)
                        #sale_value = ord.sold_quantity * 
                        data.update({
                            'id': ord.id,
                            'item_sold': ord.voucher.name,
                            'ItemType': 'Voucher',
                            'Quantity': ord.quantity,
                            'Sale_Value': ord.total_price,
                            'Commission_amount': ord.checkout.voucher_commission,
                            'Commission_Rate': rate if rate != None else 0  ,
                            'cerated_at': ord.created_at
                        })
                else:
                    rate = ord.checkout.voucher_commission_type
                    data.update({
                            'id': ord.id,
                            'item_sold': ord.voucher.name,
                            'ItemType': 'Voucher',
                            'Quantity': ord.quantity,
                            'Sale_Value': ord.total_price,
                            'Commission_amount': ord.checkout.voucher_commission,
                            'Commission_Rate': rate if rate != None else 0  ,
                            'cerated_at': ord.created_at,
                        })
                                
            return data         
            
        except Exception as err:
            return str(err)
    
    def get_location(self, obj):
        loc = obj.location.all()
        return LocationSerializer(loc, many =True ).data
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    class Meta:
        model = Employee
        fields =  ['id', 'full_name', 'service_sale_price',
                   'product_sale_price','image','location','voucher_sale_price'
                   ]
        
class ServiceGroupReport(serializers.ModelSerializer):
    # service_sale_price = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    service_target = serializers.SerializerMethodField(read_only=True)
    
    
    def get_service(self, obj):
        ser = obj.services.all()
        return ServiceReportSerializer(ser, many =True ).data
    
    def get_service_target(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            location = self.context["location"]
            ser_target = 0
            retail_target = 0
            data = {}
            
            try:
                location_id = BusinessAddress.objects.get(id = str(location))
            except:
                return
            
            service_target = ServiceTarget.objects.filter(
                service_group = obj,
                created_at__icontains = year,
                location__id =  location,
                ) 
            for ord  in service_target:
                create = str(ord.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if int(month) == match:
                    ser_target += int(ord.service_target)
                    #retail_target += int(ord.retail_target)
                    #return total
            # data.update({
            #     'service_target': service_target,
            #     'retail_target': retail_target
            # })
            
            return ser_target
            
        except Exception as err:
            return str(err)        
    class Meta:
        model = ServiceGroup
        fields = ['id','name','service','service_target']#'service_sale_price']
        
class ReportBrandSerializer(serializers.ModelSerializer): 
    product_sale_price = serializers.SerializerMethodField(read_only=True)
    brand_target = serializers.SerializerMethodField(read_only=True)

    def get_brand_target(self, obj):
        location = self.context["location"]
        retail_target = RetailTarget.objects.filter(
            brand = obj,
            location__id =  location,            
            ).order_by('-created_at').distinct()
        return RetailTargetSerializers(retail_target, many = True).data
    
    def get_product_sale_price(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            total = 0

            service_orders = ProductOrder.objects.filter(
                is_deleted=False, 
                product__brand= obj,
                created_at__icontains = year
                )
            for ord  in service_orders:
                create = str(ord.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if int(month) == match:
                    total += int(ord.total_price)
            
            return total
                
        except Exception as err:
            return str(err)
    class Meta:
        model = Brand
        fields = ['id','name', 'product_sale_price', 'brand_target']