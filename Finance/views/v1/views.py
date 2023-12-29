from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from Invoices.models import SaleInvoice
from Finance.models import Refund, Coupon
from Finance.serializers import RefundSerializer, CouponSerializer
from Finance.helpers import short_uuid

from Product.models import Product
class RefundAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        refunds = Refund.objects.select_related('client', 'business', 'location', 'refund_invoice_id', 'user').prefetch_related('refunded_products').all()
        refund_serializer = RefundSerializer(refunds, many=True)
        if not refunds:
            response_data = {
                    'success': False,
                    'status_code': 400,
                    'response':{
                        'message': 'No Records found',
                        'error_message': refund_serializer.errors,
                        'data': None
                        }
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        response_data = {
                    'success': True,
                    'status_code' : 201,
                    'response': {
                        'message': 'Record created successfully',
                        'error_message': None,
                        'data':{
                            'refund': RefundSerializer(refund_serializer.instance).data,
                            'coupon': CouponSerializer(refund_serializer.instance).data,
                        }
                    }
                }
        return Response(response_data, status=status.HTTP_200_OK)
        
        
    '''
    POST REQUEST FOR THE REFUND
    Payload formate:
        {
                "user": 1,  # ID of the staff member who generates the bills
                "client": 1,  # ID of the client
                "business": 1,  # ID of the business
                "location": 1,  # ID of the location
                "refunded_products": [
                    {
                    "product": 1,  # ID of the refunded product
                    "refunded_quantity": 2,
                    "refunded_amount": 20.00
                    },
                    {
                    "product": 2,  # ID of another refunded product
                    "refunded_quantity": 1,
                    "refunded_amount": 15.00
                    }
                ],
                "refund_type": "credit_refund",
                "reason": "Product was damaged",
                "total_refund_amount": 35.00  # This field might be calculated on the client side based on the refunded products
        }
    
    '''
    def post(self, request, *args, **kwargs):  # sourcery skip: extract-method
        try:
            user = request.user
            request.data['user'] = user.id
            serializer = RefundSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                refund_instance = serializer.save()
                client_id = request.data.get('client')
                coupon_data = {
                    'user': request.user.id,  
                    'client': client_id,
                    'refund_coupon_code': f"REFUND_{short_uuid(refund_instance.id)}",  
                    'amount': refund_instance.total_refund_amount,
                    'expiry_date': request.data.get('expiry_date'),
                    'related_refund': refund_instance.id,
                }
                try:
                    coupon_serializer = CouponSerializer(data=coupon_data)
                    coupon_serializer.is_valid(raise_exception=True)
                    coupon_serializer.save()
                except Exception as e:
                    return Response({'Error':'Error occured while Creating Coupon'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                response_data = {
                    'success': True,
                    'status_code' : 201,
                    'response': {
                        'message': 'Record created successfully',
                        'error_message': None,
                        'data':{
                            'refund': RefundSerializer(serializer.instance).data,
                            'coupon': CouponSerializer(coupon_serializer.instance).data,
                        }
                    }
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            response_data = {
                    'success': False,
                    'status_code': 400,
                    'response':{
                        'message': 'Refund not Created!',
                        'error_message': serializer.errors,
                        'data': None
                        }
            }
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # return Response({'data': request.data} , status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class RefundedCoupons(APIView):
    '''Getting coupons with the refund Data'''
    def get(self, request, *args, **kwargs):
        coupons = Coupon.objects.select_related('related_refund__business', 'related_refund__location').all()
        serializer = CouponSerializer(coupons, many=True)
        if not coupons:
            response_data = {
                    'success': False,
                    'status_code': 400,
                    'response':{
                        'message': 'No Records found',
                        'error_message': serializer.errors,
                        'data': None
                        }
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        response_data = {
                    'success': True,
                    'status_code' : 200,
                    'response': {
                        'message': 'Record created successfully',
                        'error_message': None,
                        'data': serializer.data
                    }
                }
        return Response(response_data, status=status.HTTP_200_OK)
