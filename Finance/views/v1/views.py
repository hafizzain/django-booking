from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q

from Finance.models import Refund, RefundCoupon, AllowRefunds,AllowRefundPermissionsEmployees
from Finance.serializers import RefundSerializer, CouponSerializer, AllowRefundsSerializer
from Finance.helpers import short_uuid, check_permission, check_days




@api_view(['GET'])
def check_permission_view(request):
    invoice_id = request.data.get('invoice_id')
    location = request.data.get('location')
    user = request.user.id
    try:
        if check_days(invoice_id, location) or check_permission(user, location):
            response_data = {
                            'success': True,
                            'status_code': 201,
                            'response': {
                                'message': 'Permission granted!',
                                'error_message': None,
                                'data': []
                            }
                        }
            return Response(response_data, status=status.HTTP_200_OK)
        response_data = {
                            'success': True,
                            'status_code': 404,
                            'response': {
                                'message': 'Permission Deneid!',
                                'error_message': None,
                                'data': []
                            }
                        }
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'erorr': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class RefundAPIView(APIView):

    def get(self, request, *args, **kwargs):
        refunds = Refund.objects.select_related(
            'client', 'business', 'location', 'refund_invoice_id', 'user').prefetch_related('refunded_products').all()
        refund_serializer = RefundSerializer(refunds, many=True)
        if not refunds:
            response_data = {
                'success': False,
                'status_code': 400,
                'response': {
                    'message': 'No Records found',
                    'error_message': refund_serializer.errors,
                    'data': None
                }
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        response_data = {
            'success': True,
            'status_code': 200,
            'response': {
                'message': 'Record created successfully',
                'error_message': None,
                'data': {
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
            expiry_date = request.data.get('expiry_date')
            serializer = RefundSerializer(
                data=request.data, context={'request': request})
            if serializer.is_valid():
                refund_instance = serializer.save()
                client_id = request.data.get('client')
                if expiry_date:
                    coupon_data = {
                        'user': request.user.id,
                        'client': client_id,
                        'refund_coupon_code': f"REFUND_{short_uuid(refund_instance.id)}",
                        'amount': refund_instance.total_refund_amount,
                        'expiry_date': expiry_date,
                        'related_refund': refund_instance.id,
                    }
                    try:
                        coupon_serializer = CouponSerializer(data=coupon_data)
                        coupon_serializer.is_valid(raise_exception=True)
                        coupon_serializer.save()
                    except Exception as e:
                        return Response({'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    response_data = {
                        'success': True,
                        'status_code': 201,
                        'response': {
                            'message': 'Record created successfully',
                            'error_message': None,
                            'data': {
                                'refund': RefundSerializer(serializer.instance).data,
                                'coupon': CouponSerializer(coupon_serializer.instance).data,
                            }
                        }
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {
                        'success': True,
                        'status_code': 201,
                        'response': {
                            'message': 'Refund created successfully',
                            'error_message': None,
                            'data': {
                                'refund': RefundSerializer(serializer.instance).data,
                                # 'coupon': CouponSerializer(coupon_serializer.instance).data,
                            }
                        }
                    }
                return Response(response_data, status=status.HTTP_200_OK)
            response_data = {
                'success': False,
                'status_code': 400,
                'response': {
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
        coupons = RefundCoupon.objects.select_related(
            'related_refund__business', 'related_refund__location').all()
        serializer = CouponSerializer(coupons, many=True)
        if not coupons:
            response_data = {
                'success': False,
                'status_code': 400,
                'response': {
                    'message': 'No Records found',
                    'error_message': serializer.errors,
                    'data': None
                }
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        response_data = {
            'success': True,
            'status_code': 200,
            'response': {
                'message': 'Record created successfully',
                'error_message': None,
                'data': serializer.data
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

# ==================================================== Refund Permission Work After =============================================================
class AllowRefundsAndPermissionsView(APIView):
    
    def get(self, request, format = None):
        try:
            allowed_employees = AllowRefunds.objects.select_related('location').prefetch_related('allowed_refund').all()
            serializer = AllowRefundsSerializer(allowed_employees, many=True, context={'request':request})
            if not allowed_employees:
                response_data = {
                    'status': True,
                    'status_code': 200,
                    'response': {
                        'message': 'No records found!',
                        'error_message': None,
                        'errors': [],
                        'data': [],
                    }
                }
                return Response(response_data,status=status.HTTP_200_OK)
            
            response_data = {
                    'status': True,
                    'status_code': 200,
                    'response': {
                        'message': 'Refund get successfully!',
                        'error_message': None,
                        'errors': [],
                        'data': serializer.data,

                    }
                }
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, format=None):
        '''
            POST REQUEST FOR THE REFUND PERMISSION
            Payload formate:
            {
                "location": "742cad40-eeaa-4b84-84a0-3935d4d359dd",
                "number_of_days": 56,
                "allowed_refund": [
                    {
                        "employee": "cb8c5d9d-9412-47e4-9e4d-c7b686097009"
                    },
                    {
                        "employee": "0e4990e1-9f8b-4b21-83d1-67ca01b04303"
                    }
                ]
            }
        '''    
        try:
            serializer = AllowRefundsSerializer(data=request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    'status': True,
                    'status_code': 200,
                    'response': {
                        'message': 'Permission created successfully!',
                        'error_message': None,
                        'errors': [],
                        'data': serializer.data,

                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
            response_data = {
                'status': False,
                'status_code': 200,
                'response': {
                    'message': 'Permission not Created.',
                    'error_message': None,
                    'errors': serializer.errors,
                    'data': [],
                }
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request, uuid, format=None):
        try:
            instance = AllowRefunds.objects.get(id=uuid)
            serializer = AllowRefundsSerializer(instance, data=request.data, context={'request':request})

            if serializer.is_valid():
                serializer.save()
                response_data = {
                    'status': True,
                    'status_code': 200,
                    'response': {
                        'message': 'Permissions updated successfully!',
                        'error_message': None,
                        'errors': [],
                        'data': serializer.data,
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
            response_data = {
                    'status': True,
                    'status_code': 200,
                    'response': {
                        'message': 'Error Occured!',
                        'error_message': None,
                        'errors': serializer.data,
                        'data': [],
                    }
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except AllowRefunds.DoesNotExist:
            response_data = {
                'status': False,
                'status_code': 404,
                'response': {
                    'message': 'Record not found.',
                    'error_message': None,
                    'errors': [],
                    'data': [],
                }
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, uuid, format = None):
        try:
            AllowRefunds.objects.get(id = uuid).delete()
            response_data = {
                    'status': True,
                    'status_code': 200,
                    'response': {
                        'message': 'Record deleted successfully!',
                        'error_message': None,
                        'errors': [],
                        'data': [],

                    }
                }
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

