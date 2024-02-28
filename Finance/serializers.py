from rest_framework import serializers
from django.db.models import F, Q, ExpressionWrapper, IntegerField, FloatField
from django.db import transaction

from Product.models import ProductStock
from Employee.models import Employee
from Employee.serializers import EmployeeInfoSerializer 
from Finance.models import Refund, RefundProduct, RefundServices, RefundCoupon, AllowRefunds, AllowRefundPermissionsEmployees


class RefundProductSerializer(serializers.ModelSerializer):
    refund_data  = serializers.SerializerMethodField(read_only = True)
    product_data = serializers.SerializerMethodField(read_only = True)
    
    
    def get_refund_data(self, obj):
        return {
            'refund_type':obj.refund.refund_type,
            'client': obj.refund.client.full_name if obj.refund.client else None,
            'location': obj.refund.location.address_name
        }
        
    def get_product_data(self, obj):
        return{
            'product_name': obj.product.name,
            'brand': obj.product.brand.name
            
        }
        
    class Meta: 
        model = RefundProduct
        fields = '__all__'
        read_only_fields = ['refund', 'refund_data', 'product_data']


class RefundServiceSerializer(serializers.ModelSerializer):
    refund_data  = serializers.SerializerMethodField(read_only = True)
    service_data = serializers.SerializerMethodField(read_only = True)
    
    
    def get_refund_data(self, obj):
        return {
            'refund_type':obj.refund.refund_type,
            'client': obj.refund.client.full_name if obj.refund.client else None,
            'location': obj.refund.location.address_name
        }
        
    def get_service_data(self, obj):
        return{
            'service_name': obj.service.name,
            'service group': obj.service.servicegroup_services.name
        }
        
    class Meta:
        model = RefundServices
        fields = '__all__'
        read_only_fields = ['refund','refund_data','service_data']

class RefundCouponSerializer(serializers.ModelSerializer):
    # related_refund = RefundSerializer(read_only=True)

    class Meta:
        model = RefundCoupon
        fields = '__all__'

class RefundSerializer(serializers.ModelSerializer):
    refunded_products = RefundProductSerializer(many=True)
    refunded_services = RefundServiceSerializer(many=True)
    related_refund_coupon = RefundCouponSerializer(many=True, read_only=True)

    class Meta:
        model = Refund
        fields = '__all__'

    def __product_stock_update(self, location, refunded_products_data):
        '''
        This fundtion is updating the stock if the product has the in_stock key. 
        Only thoes product record will be update in the ProductStock but the refund_quantity 
        will be update for all the products!
        '''
        try:
            [ProductStock.objects.filter(product=product_data["product"], location = location).update(refunded_quantity=ExpressionWrapper(F('refunded_quantity') + product_data["refunded_quantity"], output_field=IntegerField()))
                                for product_data in refunded_products_data]
            [ProductStock.objects.filter(product=product_data["product"], location=location).update(sold_quantity= ExpressionWrapper(F('sold_quantity') - product_data["refunded_quantity"], output_field=IntegerField()), 
                                                                                                        available_quantity=ExpressionWrapper(F('available_quantity') + product_data['refunded_quantity'], output_field=IntegerField()), 
                                                                                                        is_refunded=True)
            for product_data in refunded_products_data if product_data['in_stock'] == True]
            
            # for product_data in refunded_products_data:
            #     if product_data['in_stock'] == True:
            #         ProductStock.objects.filter(product = product_data['product'], location = location)\
            #             .update(sold_quantity = ExpressionWrapper(F('sold_quantity') + product_data['refunded_quantity'],output_field=IntegerField()),
            #                     available_quantity = ExpressionWrapper(F('available_quantity')+ product_data['refunded_quantity'], output_field=IntegerField()),
            #                     is_refunded = True)
            #     ProductStock.objects.filter(product = product_data["product"] , location = location).update(refunded_quantity =F('refunded_quantity') + product_data["refunded_quantity"])
        except Exception as e:
            return ({'error': str(e)})
        

    def create(self, validated_data):  # sourcery skip: extract-method
        request = self.context.get('request')
        location = request.data.get('location')
        refunded_products = validated_data.pop('refunded_products', [])
        refunded_services = validated_data.pop('refunded_services', [])
        
        # refunded_products = validated_data.get('refunded_products', [])
        # refunded_services = validated_data.get('refunded_services', [])
        with transaction.atomic():
            refund = Refund.objects.create(**validated_data)
            refunded_products_instances = [
                RefundProduct(refund=refund, **product_data)
                for product_data in refunded_products
            ]
            #  Creating RefundedProduct 
            RefundProduct.objects.bulk_create(refunded_products_instances)
            self.__product_stock_update(location,refunded_products)
            # Create refunded services
            refunded_services_instances = [
                RefundServices(refund=refund, **service_data)
                for service_data in refunded_services
            ]
            RefundServices.objects.bulk_create(refunded_services_instances)

        return refund



class AllowRefundPermissionsEmployeesSerializer(serializers.ModelSerializer):
    employee_data = EmployeeInfoSerializer(source = 'employee', read_only = True)

    class Meta:
        model = AllowRefundPermissionsEmployees
        fields = ['id', 'employee', 'can_refund','employee_data']

class AllowRefundsSerializer(serializers.ModelSerializer):
    allowed_refund = AllowRefundPermissionsEmployeesSerializer(many=True)
    location_name = serializers.CharField(source  = 'location.address_name', read_only = True)

    class Meta:
        model = AllowRefunds
        fields = ['id', 'location','location_name', 'number_of_days', 'allowed_refund']


    def create(self, validated_data):
        allowed_employees_data = validated_data.pop('allowed_refund', [])
        allow_refunds_instance = AllowRefunds.objects.create(**validated_data)

        employees_instances = [
            AllowRefundPermissionsEmployees(
                allowed_refund=allow_refunds_instance,
                employee=employee_data['employee'],
                can_refund = True
                )
            for employee_data in allowed_employees_data
        ]

        AllowRefundPermissionsEmployees.objects.bulk_create(employees_instances)

        return allow_refunds_instance
    
    def update(self, instance, validated_data):
        instance.location = validated_data.get('location', instance.location)
        instance.number_of_days = validated_data.get('number_of_days', instance.number_of_days)
        instance.save()
        allowed_employees_data = validated_data.get('allowed_refund', [])
        
        provided_employee_ids = {str(data['employee']) for data in allowed_employees_data}
        # print(provided_employee_ids)
        instance.allowed_refund.filter(~Q(employee_id__in=provided_employee_ids)).delete()

        for employee_data in allowed_employees_data:
            employee_id = str(employee_data['employee'])
            employee_instance = Employee.objects.get(id=employee_id)

            obj, created = AllowRefundPermissionsEmployees.objects.update_or_create(
                allowed_refund=instance,
                employee=employee_instance,
                defaults={'can_refund': employee_data.get('can_refund', False)}
            )

        return instance
    
