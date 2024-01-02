from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from Invoices.models import SaleInvoice
from Finance.models import Refund, RefundCoupon
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
            "business": "fb06734e-5f9b-4bab-bc43-c803d3c5a5db",
            "user": 2,
            "location": "d956e922-089f-4d61-8079-fe9ed76ec053",
            "refunded_products": [
            {
            "product": "6c7ffa6a-278a-4973-a609-7b7f0d86ac21",
            "refunded_quantity": 1,
            "refunded_amount": 100.00,
            "in_stock": true
            },
            {
            "product": "1f67cf1f-c63b-42f3-bb38-4226da4a20fa",
            "refunded_quantity": 1,
            "refunded_amount": 100.00
            }
            ],
            "refunded_services": [
            {
            "service": "d47cdbda-5965-4e06-9168-b3284d38c25f",
            "refunded_amount": 100.00
            }
            ],
            "refund_type": "credit_refund",
            "expiry_date": "2023-12-30",
            "total_refund_amount": 100
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
                    return Response({'Error':'Error occured while Creating Coupon', 'Errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
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
                return Response(response_data, status=status.HTTP_200_OK)
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
        coupons = RefundCoupon.objects.select_related('related_refund__business', 'related_refund__location').all()
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
