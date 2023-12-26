from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from Finance.models import Refund, Client
from Finance.serializers import RefundSerializer, CouponSerializer
from Finance.helpers import short_uuid

class RefundAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        refunds = Refund.objects.select_related('client', 'business', 'location', 'refund_invoice_id', 'user').prefetch_related('refunded_products').all()
        refund_serializer = RefundSerializer(refunds, many=True)
        
        if not refunds:
            return Response({"error": "No refunds found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({'refunds': refund_serializer.data}, status=status.HTTP_200_OK)
        
        
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
            serializer = RefundSerializer(data=request.data)
            if serializer.is_valid():
                refund_instance = serializer.save()
                
                client_id = request.data.get('client')
                client = get_object_or_404(Client, pk=client_id)

                coupon_data = {
                    'user': request.user,  
                    'client': client,
                    'refund_coupon_code': f"REFUND_{short_uuid(refund_instance.id)}",  
                    'amount': refund_instance.total_refund_amount,
                    'expiry_date': refund_instance.expiry,
                    'related_refund': refund_instance,
                }
                
                coupon_serializer = CouponSerializer(data=coupon_data)
                coupon_serializer.is_valid(raise_exception=True)
                coupon_serializer.save()

                response_data = {
                    'message': 'Record created successfully',
                    'refund': RefundSerializer(refund_instance).data,
                    'coupon': CouponSerializer(coupon_serializer.instance).data,
                }

                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
