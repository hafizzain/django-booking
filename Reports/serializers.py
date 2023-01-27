from datetime import date, datetime
from rest_framework import serializers
from Appointment.serializers import LocationSerializer
from Employee.models import Employee
from Product.Constants.index import tenant_media_base_url

from Order.models import ProductOrder, ServiceOrder, VoucherOrder
from Sale.serializers import ProductOrderSerializer
from TragetControl.models import StaffTarget
from TragetControl.serializers import StaffTargetSerializers


class ServiceOrderSerializer(serializers.ModelSerializer):
    # client = serializers.SerializerMethodField(read_only=True)
    # service = serializers.SerializerMethodField(read_only=True)
    # location = serializers.SerializerMethodField(read_only=True)
    # member  = serializers.SerializerMethodField(read_only=True)
    user  = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    
    def get_order_type(self, obj):
        return 'Service'
    
    # def get_service(self, obj):
    #     try:
    #         serializers = ServiceSearchSerializer(obj.service).data
    #         return serializers
    #     except Exception as err:
    #         return None
        
    # def get_location(self, obj):
    #     try:
    #         serializers = LocationSerializer(obj.location).data
    #         return serializers
    #     except Exception as err:
    #         return None
    
    # def get_member(self, obj):
    #     try:
    #         serializers = MemberSerializer(obj.member, context=self.context).data
    #         return serializers
    #     except Exception as err:
    #         return None
        
    # def get_client(self, obj):
    #     try:
    #         serializers = ClientSerializer(obj.client).data
    #         return serializers
    #     except Exception as err:
    #         return None
        
    def get_user(self, obj):
        try:
            return obj.user.full_name
        except Exception as err:
            return None
    class Meta:
        model = ServiceOrder
        fields = ('__all__')
        #fields = ['id', 'client','quantity', 'service','created_at' ,'user',
                #   'duration', 'location', 'member', 'total_price',
                #   'payment_type','tip','gst', 'order_type','created_at'
                #   ]



class ReportsEmployeSerializer(serializers.ModelSerializer):    
    image = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField(read_only=True)
    
    service_sale_price = serializers.SerializerMethodField(read_only=True)
    product_sale_price = serializers.SerializerMethodField(read_only=True)
    
    staff_target = serializers.SerializerMethodField(read_only=True)
        
    def get_product_sale_price(self, obj):
        try:
            
            # product_order = ProductOrder.objects.filter(is_deleted=False, member = obj).order_by('-created_at')
            
            # serialized = ProductOrderSerializer(product_order,  many=True, context=self.context ).data
            # return serialized
            month = self.context["month"]
            year = self.context["year"]
            total = 0
            test = 0
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
                    test = test + 5
                    #return total
            
            return f'{total}'
                
        except Exception as err:
            return str(err)
    
    def get_service_sale_price(self, obj):
        try:
            # service_orders = ServiceOrder.objects.filter(is_deleted=False).order_by('-created_at')
            # serialized = ServiceOrderSerializer(service_orders,  many=True, context=self.context).data
            # return serialized
            month = self.context["month"]
            year = self.context["year"]
            total = 0
            test = 0
            service_orders = ServiceOrder.objects.filter(is_deleted=False, 
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
        
    def get_staff_target(self, obj):
        try:
            # staff_target = StaffTarget.objects.filter(employee = obj)  
            # serializer = StaffTargetSerializers(staff_target, many = True, context=self.context).data
            # return serializer
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
                if int(month) == match:
                    service_target += int(ord.service_target)
                    retail_target += int(ord.retail_target)
                    #return total
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
                # range_start = date(range_start)
                # range_end = date(range_end)
                range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
                range_end = datetime.strptime(range_end, "%Y-%m-%d").date()
                                          
            total = 0
            service_commission = 0
            
            product_commission = 0
            voucher_commission = 0
            data = {}
            
            service_orders = ProductOrder.objects.filter(
                is_deleted=False, 
                member = obj, 
                #created_at__icontains = year
                )
            for ord  in service_orders:
                create = str(ord.created_at)
                created_at = datetime.strptime(create, "%Y-%m-%d").date()
                #match = create.split(" ")[0]#.split("-")[1])
                return create
                # if range_start:
                #     return created_at
                #     if range_start >= created_at  and created_at <= range_end:
                #         total += int(ord.total_price)
                #         service_commission += ord.checkout.service_commission
                #         product_commission += ord.checkout.product_commission
                #         voucher_commission += ord.checkout.voucher_commission
                #     #total = 3
                # else:
                #     total += int(ord.total_price)
                #     service_commission += ord.checkout.service_commission
                #     product_commission += ord.checkout.product_commission
                #     voucher_commission += ord.checkout.voucher_commission

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
            # service_orders = ServiceOrder.objects.filter(is_deleted=False).order_by('-created_at')
            # serialized = ServiceOrderSerializer(service_orders,  many=True, context=self.context).data
            # return serialized
            range_start = self.context["range_start"]
            range_end = self.context["range_end"]
            year = self.context["year"]
            total = 0
            test = 0
            service_orders = ServiceOrder.objects.filter(is_deleted=False, 
                        member = obj,
                        #created_at__icontains = year
                        )
            for ord  in service_orders:
                create = str(ord.created_at)
                ord.checkout.service_commission
                match = int(create.split(" ")[0].split("-")[1])
                if range_start is not None:
                    pass
                    #total += int(ord.total_price)
                else:
                    total += int(ord.total_price)
                                
            return total         
            
        except Exception as err:
            return str(err)
        
    def get_voucher_sale_price(self, obj):
        try:
            range_start = self.context["range_start"]
            range_end = self.context["range_end"]
            year = self.context["year"]
            total = 0
            test = 0
            service_orders = VoucherOrder.objects.filter(is_deleted=False, 
                        member = obj,
                        #created_at__icontains = year
                        )
            for ord  in service_orders:
                create = str(ord.created_at)
                match = int(create.split(" ")[0].split("-")[1])
                if range_start is not None:
                    pass
                    #total += int(ord.total_price)
                else:
                    total += int(ord.total_price)
                                
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