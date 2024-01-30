from SaleRecords.models import SaleRecords
from Invoices.models import SaleInvoice

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from SaleRecords.serializers import *


class SaleRecordViews(APIView):
    def get(self, request, *args, **kwargs):
        try:
            sale_record = SaleRecords.objects.all()
            response = {
                'success': True,
                'status_code': 200,
                'response': {
                            'message': 'Record fetched successfully!',
                            'error_message': None,
                            'data': {
                                'checkout': SaleRecordSerializer(sale_record, many = True).data,
                                # 'coupon': CouponSerializer(coupon_serializer.instance).data,
                                # 'invoice': InvoiceSerializer(invoice).data
                            }
                        }
            }
            return Response(response)
        except Exception as e:
            return Response({'error' : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            request.data['user'] = user.id
            serializer = SaleRecordSerializer(data=request.data, context = {'request': request})
            if serializer.is_valid():
                sale_record = serializer.save()
                
                invoice = SaleInvoice.objects.create(
                    user=user,
                    client=sale_record.client,
                    location=sale_record.location,
                    appointment=request.data.get('appointment', None),
                    appointment_service=request.data.get('appointment_service', None),
                    payment_type=request.data.get('payment_type', None),
                    # payment_methods=request.data.get('payment_methods_records'),

                    # tip=f'{request.data.get("tip")}' if request.data.get("tip") else 0,
                    invoice_type='order',
                    checkout_type=f'{request.data.get("checkout_type")}' if request.data.get("checkout_type") else 'sale',

                    service=f'{request.data.get("service")}' if request.data.get("service") else '',
                    member=f'{request.data.get("member")}' if request.data.get("member") else '',
                    # business_address=f'{request.data.get("location")}' if request.data.get("location") else '',
                    gst=f'{request.data.get("gst")}' if request.data.get("gst") else 0,
                    gst_price=f'{request.data.get("gst_price")}' if request.data.get("gst_price") else 0,
                    service_price=f'{request.data.get("service_price")}' if request.data.get("service_price") else 0,
                    total_price=f'{request.data.get("total_price")}' if request.data.get("total_price") else 0,
                    service_commission=f'{request.data.get("service_commission")}' if request.data.get("service_commission") else 0,
                    service_commission_type=f'{request.data.get("service_commission_type")}' if request.data.get("service_commission_type") else '',
                    checkout=sale_record.id,
                )
                invoice_serializer = SaleInvoiceSerializer(data=invoice)
                if invoice_serializer.is_valid():
                    invoice_serializer.save()
                    sale_record.invoice = invoice_serializer.instance
                    sale_record.save()
                
                
                response_data = {
                        'success': True,
                        'status_code': 200,
                        'response': {
                            'message': 'Checkout created successfully!',
                            'error_message': None,
                            'data': {
                                'checkout': SaleRecordSerializer(sale_record).data,
                                # 'coupon': CouponSerializer(coupon_serializer.instance).data,
                                # 'invoice': InvoiceSerializer(invoice).data
                            }
                        }
                    }
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)