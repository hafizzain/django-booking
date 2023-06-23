from datetime import date, datetime
from Product.models import Brand
from Utility.models import ExceptionRecord
from rest_framework import serializers
from Appointment.models import AppointmentCheckout, AppointmentService
from Appointment.serializers import LocationSerializer
from Business.models import BusinessAddress
from Employee.models import Employee, EmployeeCommission
from Product.Constants.index import tenant_media_base_url
from django.db.models import Sum
from django.db.models.functions import Coalesce

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
                created_at__year = year,
                created_at__month = month,
                )
            for ord  in service_orders:
                # create = str(ord.created_at)
                # match = int(create.split(" ")[0].split("-")[1])
                # if int(month) == match:
                #     total += int(ord.total_price)
                price = 0
                if ord.discount_price:
                    price = ord.discount_price
                else:
                    price = ord.total_price
                
                total += float(price) * float(ord.quantity)
            
            return f'{total}'
                
        except Exception as err:
            return str(err)
    
    def get_service_sale_price(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            total = 0
            app = AppointmentService.objects.filter(
                member = obj,
                appointment_status = 'Done',
                created_at__icontains = year
            )
        
            service_orders = ServiceOrder.objects.filter(
                is_deleted=False, 
                member = obj,
                created_at__year = year,
                created_at__month = month,
            )
            for appointment in app:
                create = str(appointment.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if int(month) == match:
                    total += int(appointment.price)
                    
            for ord in service_orders:
                # create = str(ord.created_at)
                # match = int(create.split(" ")[0].split("-")[1])
                # if int(month) == match:
                #     total += int(ord.total_price)
                price = 0
                if ord.discount_price:
                    price = ord.discount_price
                else:
                    price = ord.total_price
                
                total += float(price) * float(ord.quantity)
                                
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
            
            date_str = f'{month}-{year}'
            date_obj = datetime.strptime(date_str, '%m-%Y')
            
            staff_target = StaffTarget.objects.filter(
                employee = obj,
                #created_at__icontains = date_obj                
                ) 
            for ord  in staff_target:
                created_date = ord.year.date() 
                if created_date.month == date_obj.month and created_date.year == date_obj.year:
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
    
    def get_product_sale_price(self,obj):
        range_start = self.context.get("range_start", None)
        range_end = self.context.get("range_end", None)

        query = {}

        if range_start and range_end:
            query['created_at__range'] = (range_start, range_end)


        employee_commissions = EmployeeCommission.objects.filter(
            employee = obj,
            is_active = True,
            **query
        )

        commission_total = 0
        product_commission = 0
        service_commissions = 0
        vouchers_commissions = 0
        
        total_product_price = 0

        for commission in employee_commissions:
            full_commission = commission.single_item_commission
            # full_commission = commission.full_commission
            commission_total += full_commission

            # Mannaging Product Commission
            if commission.commission_category == 'Retail':
                product_commission += full_commission
                total_product_price += commission.sale_value

            # Mannaging Services Commission
            elif commission.commission_category == 'Service':
                service_commissions += full_commission

            # Mannaging Vouchers Commission
            elif commission.commission_category == 'Voucher':
                vouchers_commissions += full_commission

        data = {
            'product_sale_price': total_product_price,
            'commission_total': commission_total,
            'service_commission': service_commissions,
            'product_commission': product_commission,
            'voucher_commission': vouchers_commissions,
        }
        return data
        
        # app = AppointmentService.objects.filter(
        #     member=obj,
        #     appointment_status='Done',
        # )
        # if range_start:
        #     range_start = datetime.strptime(range_start, '%Y-%m-%d').date()
        #     range_end = datetime.strptime(range_end, '%Y-%m-%d').date()
        #     app = app.filter(created_at__range=(range_start, range_end))
        # total_service_commission = app.aggregate(Sum('service_commission'))['service_commission__sum'] or 0

        # product_orders = ProductOrder.objects.filter(
        #     is_deleted=False,
        #     member=obj,
        # )
        # if range_start:
        #     product_orders = product_orders.filter(created_at__range=(range_start, range_end))
        # total_product_price = product_orders.aggregate(Sum('checkout__total_product_price'))['checkout__total_product_price__sum'] or 0
        # product_commission = product_orders.aggregate(Sum('checkout__product_commission'))['checkout__product_commission__sum'] or 0

        # service_orders = ServiceOrder.objects.filter(
        #     is_deleted=False,
        #     member=obj,
        # )
        # if range_start:
        #     service_orders = service_orders.filter(created_at__range=(range_start, range_end))
        # service_commission = service_orders.aggregate(Sum('checkout__service_commission'))['checkout__service_commission__sum'] or 0

        # voucher_orders = VoucherOrder.objects.filter(
        #     is_deleted=False,
        #     member=obj,
        # )
        # if range_start:
        #     voucher_orders = voucher_orders.filter(created_at__range=(range_start, range_end))
        # voucher_commission = voucher_orders.aggregate(Sum('checkout__voucher_commission'))['checkout__voucher_commission__sum'] or 0

        # commission_total = total_service_commission + product_commission + voucher_commission
        
        # ser_commission = int(service_commission) + int(total_service_commission)
        # data = {
        #     'product_sale_price': total_product_price,
        #     'commission_total': commission_total,
        #     'service_commission': ser_commission,
        #     'product_commission': product_commission,
        #     'voucher_commission': voucher_commission,
        # }
        # return data
            
    def get_service_sale_price(self, obj):
        range_start = self.context.get("range_start")
        range_end = self.context.get("range_end")
        

        query = {}

        if range_start and range_end:
            query['created_at__range'] = (range_start, range_end)

        # if range_start:
        #     range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
        # if range_end:
        #     range_end = datetime.strptime(range_end, "%Y-%m-%d").date()
            
        # appointments_total = 0
        # service_orders_total = 0
        
        # if range_start and range_end:
        #     appointments_total = AppointmentService.objects.filter(
        #         member=obj,
        #         appointment_status='Done',
        #         created_at__range=(range_start, range_end)
        #     ).aggregate(total=Coalesce(Sum('price'), 0))['total']
            
        #     service_orders_total = ServiceOrder.objects.filter(
        #         is_deleted=False,
        #         member=obj,
        #         created_at__range=(range_start, range_end)
        #     ).aggregate(total=Coalesce(Sum('checkout__total_service_price'), 0))['total']
        # else:
        #     appointments_total = AppointmentService.objects.filter(
        #         member=obj,
        #         appointment_status='Done'
        #     ).aggregate(total=Coalesce(Sum('price'), 0))['total']
            
        #     service_orders_total = ServiceOrder.objects.filter(
        #         is_deleted=False,
        #         member=obj
        #     ).aggregate(total=Coalesce(Sum('checkout__total_service_price'), 0))['total']
        
        # total = appointments_total + service_orders_total

        services_commissions = EmployeeCommission.objects.filter(
            employee = obj,
            commission_category = 'Service',
            is_active = True,
            **query
        )

        total_sale = sum([(commission.sale_value * commission.quantity) for commission in services_commissions])
        self.total_service_sale_price = total_sale
        
        return self.total_service_sale_price


    
    # def get_service_sale_price(self, obj):
    #     try:
    #         range_start = self.context["range_start"]
    #         range_end = self.context["range_end"]
    #         year = self.context["year"]
            
    #         if range_start:
    #             range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
    #             range_end = datetime.strptime(range_end, "%Y-%m-%d").date()
            
    #         total = 0
    #         service_orders = ServiceOrder.objects.filter(is_deleted=False, 
    #                     member = obj,
    #                     #created_at__icontains = year
    #                     )
    #         app   = AppointmentService.objects.filter(
    #             member = obj,
    #             appointment_status = 'Done',
    #             #created_at__icontains = year
    #         )
    #         for appointment  in app:                
    #             create = str(appointment.created_at)
    #             created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
                
    #             if range_start:
    #                 if range_start >= created_at  and created_at <= range_end:
    #                     total += int(appointment.price)
    #             else:
    #                 total += int(appointment.price)
                    
    #         for ord  in service_orders:                
    #             create = str(ord.created_at)
    #             created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
                
    #             if range_start:
    #                 if range_start >= created_at  and created_at <= range_end:
    #                     total += int(ord.checkout.total_service_price)
    #             else:
    #                 total += int(ord.checkout.total_service_price)
                                          
    #         return total         
            
    #     except Exception as err:
    #         return str(err)
        
    def get_voucher_sale_price(self, obj):
        range_start = self.context["range_start"]
        range_end = self.context["range_end"]            

        query = {}

        if range_start and range_end:
            query['created_at__range'] = (range_start, range_end)

        # try:
        #     year = self.context["year"]
            
        #     if range_start:
        #         range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
        #         range_end = datetime.strptime(range_end, "%Y-%m-%d").date()
            
        #     total = 0
        #     service_orders = VoucherOrder.objects.filter(is_deleted=False, 
        #                 member = obj,
        #                 #created_at__icontains = year
        #                 )
        #     for ord  in service_orders:
        #         create = str(ord.created_at)
        #         created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
                
        #         if range_start:
        #             if range_start >= created_at  and created_at <= range_end:
        #                 total += int(ord.checkout.total_voucher_price)
        #         else:
        #             total += int(ord.checkout.total_voucher_price)
                                
        #     return total         
            
        # except Exception as err:
        #     return str(err)    
        vouchers_commissions = EmployeeCommission.objects.filter(
            employee = obj,
            commission_category = 'Voucher',
            is_active = True,
            **query
        )
        total_sale = sum([(commission.sale_value * commission.quantity) for commission in vouchers_commissions])
        self.total_voucher_sale_price = total_sale
        
        return self.total_voucher_sale_price
    
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
        fields = [
            'id', 
            'employee_id',
            'is_active',
            'full_name',
            'image',
            'location',
            'created_at',
            'service_sale_price',
            'voucher_sale_price',
            'product_sale_price',
        ]
        
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
    
    # def get_service_sale_price(self, obj):
    #     try:
    #         month = self.context["month"]
    #         year = self.context["year"]
    #         total = 0
            
    #         app   = AppointmentService.objects.filter(
    #             business_address = obj,
    #             appointment_status = 'Done',
    #         )
    #         service_orders = ServiceOrder.objects.filter(is_deleted=False,
    #                     location = obj,
    #                     created_at__icontains = year
    #                     )
            
    #         for ord  in app:
    #             create = str(ord.created_at)
    #             match = int(create.split(" ")[0].split("-")[1])
    #             if int(month) == match:
    #                 total += int(ord.price)
            
    #         for ord  in service_orders:
    #             create = str(ord.created_at)
    #             match = int(create.split(" ")[0].split("-")[1])
    #             if int(month) == match:
    #                 total += int(ord.checkout.total_service_price)
                                
    #         return total         
            
    #     except Exception as err:
    #         return str(err)
    
    def get_service_sale_price(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            total = 0

            app = AppointmentService.objects.filter(
                business_address=obj,
                appointment_status='Done',
            )
            service_orders = ServiceOrder.objects.filter(
                is_deleted=False,
                location=obj,
                created_at__icontains=year
            )

            for ord in app:
                create = str(ord.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if int(month) == match:
                    total += int(ord.price) if ord.price is not None else 0

            for ord in service_orders:
                # create = str(ord.created_at)
                # match = int(create.split(" ")[0].split("-")[1])
                # if int(month) == match:
                #     total += int(ord.checkout.total_service_price) if ord.checkout.total_service_price is not None else 0
                price = 0
                if ord.discount_price:
                    price = ord.discount_price
                else:
                    price = ord.total_price
                total += (float(ord.quantity) * float(price))

            return total

        except Exception as err:
            return str(err)
    
    # def get_product_sale_price(self, obj):
    #     try:
    #         month = self.context["month"]
    #         year = self.context["year"]
    #         total = 0

    #         service_orders = ProductOrder.objects.filter(
    #             is_deleted=False, 
    #             location = obj,
    #             created_at__icontains = year
    #             )
    #         for ord  in service_orders:
    #             create = str(ord.created_at)
    #             match = int(create.split(" ")[0].split("-")[1])
    #             if int(month) == match:
    #                 total += int(ord.checkout.total_product_price)
            
    #         return total
                
    #     except Exception as err:
    #         return str(err)
        
    # def get_product_sale_price(self, obj):
    #     try:
    #         month = self.context["month"]
    #         year = self.context["year"]
    #         total = 0

    #         service_orders = ProductOrder.objects.filter(
    #             is_deleted=False, 
    #             location=obj,
    #             created_at__icontains=year
    #         )
    #         for ord in service_orders:
    #             create = str(ord.created_at)
    #             match = int(create.split(" ")[0].split("-")[1])
    #             if int(month) == match:
    #                 total += int(ord.checkout.total_product_price) or 0  # Use 0 as default value if None
                
    #         return total

    #     except Exception as err:
    #         return str(err)

    def get_product_sale_price(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            total = 0

            service_orders = ProductOrder.objects.filter(
                is_deleted = False, 
                location = obj,
                created_at__year = year,
                created_at__month = month,
            )
            for ord in service_orders:
                # create = str(ord.created_at)
                # match = int(create.split(" ")[0].split("-")[1])
                # if int(month) == match:
                #     total += int(ord.checkout.total_product_price) if ord.checkout.total_product_price is not None else 0
                price = 0
                if ord.discount_price:
                    price = ord.discount_price
                else:
                    price = ord.total_price
                total += (float(ord.quantity) * float(price))

            return total

        except Exception as err:
            return str(err)
    

    # def get_voucher_sale_price(self, obj):
    #     try:
    #         month = self.context["month"]
    #         year = self.context["year"]
    #         total = 0

    #         service_orders = VoucherOrder.objects.filter(
    #             is_deleted=False, 
    #             location = obj,
    #             created_at__icontains = year,
    #             )
    #         for ord  in service_orders:
    #             create = str(ord.created_at)
    #             match = int(create.split(" ")[0].split("-")[1])
    #             if int(month) == match:
    #                 total += int(ord.checkout.total_voucher_price)
            
    #         return total
                
    #     except Exception as err:
    #         return str(err)

    def get_voucher_sale_price(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            total = 0

            service_orders = VoucherOrder.objects.filter(
                is_deleted = False,
                location = obj,
                created_at__year = year,
                created_at__month = month,
            )
            for ord in service_orders:
                # create = str(ord.created_at)
                # match = int(create.split(" ")[0].split("-")[1])
                # if int(month) == match:
                    # total += int(ord.checkout.total_voucher_price) if ord.checkout.total_voucher_price is not None else 0
                price = 0
                if ord.discount_price:
                    price = ord.discount_price
                else:
                    price = ord.total_price
                total += (float(ord.quantity) * float(price))

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
                created_at__year = year,
                created_at__month = month,
            )
            for ord  in service_orders:
                # create = str(ord.created_at)
                # match = int(create.split(" ")[0].split("-")[1])
                # if int(month) == match:
                #     total += int(ord.checkout.total_membership_price)
                total += (ord.quantity * ord.total_price)
            
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
    # services_sales = serializers.SerializerMethodField(read_only=True)
    # appointment_sales = serializers.SerializerMethodField(read_only=True)
    # total_service_sales = serializers.SerializerMethodField(read_only=True)

    # def get_appointment_sales(self, obj):
    #     return obj.appointment_sales
    
    # def get_total_service_sales(self, obj):
    #     return obj.appointment_sales + obj.services_sales
    
    # def get_services_sales(self, obj):
    #     return obj.services_sales
    
    def get_service(self, obj):
        ser = obj.services.all()
        return ServiceReportSerializer(ser, many =True ).data
    
    def get_service_target(self, obj):
        try:
            month = self.context["month"]
            year = self.context["year"]
            location = self.context["location"]
            ser_target = 0
            
            date_str = f'{month}-{year}'
            date_obj = datetime.strptime(date_str, '%m-%Y')
                        
            service_target = ServiceTarget.objects.filter(
                service_group = obj,
                created_at__icontains = year,
                location__id =  location,
                ) 
            for ord  in service_target:
                created_date = ord.year.date() 
                if created_date.month == date_obj.month and created_date.year == date_obj.year:
                    ser_target += int(ord.service_target)            
            return ser_target
            
        except Exception as err:
            return str(err)        
    class Meta:
        model = ServiceGroup
        fields = ['id','name','service','service_target']
        
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
    
    # def get_product_sale_price(self, obj):
    #     try:
    #         location = self.context["location"]
    #         month = self.context["month"]
    #         year = self.context["year"]
    #         total = 0

    #         service_orders = ProductOrder.objects.filter(
    #             is_deleted=False, 
    #             product__brand= obj,
    #             created_at__icontains = year,
    #             location__id =  location,  
    #             )
    #         for ord  in service_orders:
    #             create = str(ord.created_at)
    #             match = int(create.split(" ")[0].split("-")[1])
    #             if int(month) == match:
    #                 total += int(ord.checkout.total_product_price)
            
    #         return total
                
    #     except Exception as err:
    #         return str(err)

    def get_product_sale_price(self, obj):
        try:
            location = self.context["location"]
            month = self.context["month"]
            year = self.context["year"]
            total = 0

            service_orders = ProductOrder.objects.filter(
                is_deleted = False, 
                product__brand = obj,
                created_at__year = year,
                created_at__month = month,
                location__id = location,
            )
            
            for ord in service_orders:
                # create = str(ord.created_at)
                # match = int(create.split(" ")[0].split("-")[1])
                # if int(month) == match:
                price = 0
                if ord.discount_price:
                    price = ord.discount_price
                else:
                    price = ord.total_price

                total += (float(price) * float(ord.quantity))

                # if ord.checkout and ord.checkout.total_product_price:
                #     total += int(ord.checkout.total_product_price)
            
            return total

        except Exception as err:
            return str(err)
    class Meta:
        model = Brand
        fields = ['id','name', 'product_sale_price', 'brand_target']


class EmployeeCommissionReportsSerializer(serializers.ModelSerializer):

    employee = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    sale = serializers.SerializerMethodField()
    order_type  = serializers.SerializerMethodField(read_only=True)
    commission  = serializers.SerializerMethodField(read_only=True)
    commission_rate  = serializers.SerializerMethodField(read_only=True)


    def get_employee(self, commission_instance):
        if commission_instance.employee:
            return {
                'full_name' : f'{commission_instance.employee.full_name}',
                'id' : f'{commission_instance.employee.id}',
            }
    
        return None

    def get_location(self, commission_instance):
        if commission_instance.location:
            return {
                'name' : f'{commission_instance.location.address_name}',
                'id' : f'{commission_instance.location.id}',
            }
    
        return None

    def get_order_type(self, commission_instance):
        return 'Service'

    def get_commission(self, commission_instance):
        return commission_instance.commission_amount
        # return commission_instance.full_commission

    def get_commission_rate(self, commission_instance):
        return f'{commission_instance.commission_rate} {commission_instance.symbol}'


    def get_sale(self, commission_instance):
        return {
            "created_at": commission_instance.created_at,
            "id": f'{commission_instance.id}',
            "quantity": commission_instance.quantity,
            "name": commission_instance.item_name,
            "price": commission_instance.total_price,
            # "price": commission_instance.sale_value,
            "order_type": commission_instance.commission_category,
            "payment_type": "Cash",
            "tip": commission_instance.tip,
            "client": ""
        }


    class Meta:
        model = EmployeeCommission
        fields = ['id', 'location', 'employee', 'order_type', 'commission_rate', 'commission', 'created_at', 'sale']
        #  'location', 'commission_rate',