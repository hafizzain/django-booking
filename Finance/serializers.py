from rest_framework import serializers
from django.db.models import F, Q
from django.db import transaction

from Product.models import ProductStock
from Employee.models import Employee
from Employee.serializers import EmployeeInfoSerializer 
from Finance.models import Refund, RefundProduct, RefundServices, RefundCoupon, AllowRefunds, AllowRefundPermissionsEmployees


class RefundProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundProduct
        fields = '__all__'
        read_only_fields = ['refund']


class RefundServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundServices
        fields = '__all__'
        read_only_fields = ['refund']

class CouponSerializer(serializers.ModelSerializer):
    # related_refund = RefundSerializer(read_only=True)

    class Meta:
        model = RefundCoupon
        fields = '__all__'

class RefundSerializer(serializers.ModelSerializer):
    refunded_products = RefundProductSerializer(many=True, read_only = True)
    refunded_services = RefundServiceSerializer(many=True, read_only=True)
    related_refund_coupon = CouponSerializer(many=True, read_only=True)

    class Meta:
        model = Refund
        fields = '__all__'

    def product_stock_update(self, location, refunded_products_data):
        '''
        This fundtion is updating the stock if the product has the in_stock key. 
        Only thoes product record will be update in the ProductStock but the refund_quantity 
        will be update for all the products!
        '''
        try:
            [ProductStock.objects.filter(product_id=product_data["product"], location_id = location).update(refunded_quantity=F('refunded_quantity') + product_data["refunded_quantity"])
                                for product_data in refunded_products_data]
            [ProductStock.objects.filter(product_id=product_data["product"], location_id=location).update(sold_quantity=F('sold_quantity') - product_data["refunded_quantity"], 
                                                                                                        available_quantity=F('available_quantity') + product_data['refunded_quantity'], 
                                                                                                        is_refunded=True)
            for product_data in refunded_products_data if product_data['in_stock'] == True]
        except Exception as e:
            return ({'error': str(e)})
        return True

    def create(self, validated_data):  # sourcery skip: extract-method
        request = self.context.get('request')
        location = request.data.get('location')
        refunded_products_data = request.data.get('refunded_products', [])
        refunded_services_data = request.data.get('refunded_services', [])
        with transaction.atomic():
            refund = Refund.objects.create(**validated_data)
            refunded_products_instances = [
                RefundProduct(refund=refund, **product_data)
                for product_data in refunded_products_data
            ]
            #  Creating RefundedProduct 
            RefundProduct.objects.bulk_create(refunded_products_instances)
            self.product_stock_update(location,refunded_products_data)
            # Create refunded services
            refunded_services_instances = [
                RefundServices(refund=refund, **service_data)
                for service_data in refunded_services_data
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
    
