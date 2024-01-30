from SaleRecords.models import SaleRecords
from Invoices.models import SaleInvoice

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from SaleRecords.serializers import *

class SaleRecordViews(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            request.data['user'] = user.id
            # client_id = request.data.get('client')  # Ensure 'client' is present in request data
            # if not client_id:
            #     return Response({"error": "'client' is required in the request data."}, status=status.HTTP_400_BAD_REQUEST)
            # return Response({'success':'Yeaaahhhhhh'})
            serializer = SaleRecordSerializer(data=request.data, context = {'request': request})
            if serializer.is_valid():
                sale_record = serializer.save()
                
                invoice = SaleInvoice.objects.create(
                    user = request.user,
                    client=request.client if request.client else None,
                    location = request.location if request.location else None,
                    appointment=request.appointment if request.appointment else None,
                    appointment_service=request.appointment_service if request.appointment_service else None,
                    payment_type=request.payment_type if request.payment_type else None,
                    # payment_methods = request.payment_methods_records if request.payment_methods_records else None,

                    tip = f'{request.tip}' if request.tip else 0,
                    invoice_type='order',
                    checkout_type=f'{request.checkout_type}' if request.checkout_type else 'sale',

                    service=f'{request.service}' if request.service else '',
                    member=f'{request.member}' if request.member else '',
                    business_address=f'{request.location}' if request.location else '',
                    gst=f'{request.gst}' if request.gst else '',
                    gst_price=f'{request.gst_price}' if request.gst_price else '',
                    service_price=f'{request.service_price}' if request.service_price else 0,
                    total_price=f'{request.total_price}' if request.total_price else 0,
                    service_commission=f'{request.service_commission}' if request.service_commission else 0,
                    service_commission_type=f'{request.service_commission_type}' if request.service_commission_type else '',
                    checkout=sale_record.id,
                )
                invoice.save()
                
                response_data = {
                        'success': True,
                        'status_code': 200,
                        'response': {
                            'message': 'Checkout created successfully!',
                            'error_message': None,
                            'data': {
                                'checkout': serializer.data,
                                # 'coupon': CouponSerializer(coupon_serializer.instance).data,
                                'invoice': InvoiceSerializer(invoice).data
                            }
                        }
                    }
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)