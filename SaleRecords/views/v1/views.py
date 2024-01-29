from SaleRecords.models import SaleRecords

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from SaleRecords.serializers import SaleRecordSerializer


class SaleRecordViews(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            request.data['user'] = user.id
            serializer = SaleRecordSerializer(data=request.data, context = {'request': request})
            if serializer.is_valid():
                sale_record = serializer.save()
                
                response_data = {
                        'success': True,
                        'status_code': 201,
                        'response': {
                            'message': 'Checkout created successfully!',
                            'error_message': None,
                            'data': {
                                'checkout': serializer.data,
                                # 'coupon': CouponSerializer(coupon_serializer.instance).data,
                                # 'invoice': SaleInvoiceSerializer(newInvoice).data
                            }
                        }
                    }
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)