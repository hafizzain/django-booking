
from Invoices.models import SaleInvoice

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view


from SaleRecords.helpers import matching_records, loyalty_points_update
from Client.Constants.client_order_email import send_order_email, send_membership_order_email

from SaleRecords.serializers import *
from Business.serializers.v1_serializers import BusinessAddressSerilaizer


class SaleRecordViews(APIView):
    pagination_class = PageNumberPagination
    page_size = 10
    
    def get(self, request, *args, **kwargs):
        try:
            
            location = request.GET.get('location', None)
            range_start = request.GET.get('range_start', None)
            range_end = request.GET.get('range_end', None)
            client = request.GET.get('client',None)
            search_text = request.GET.get('search_text', None)
            service = request.GET.get('service', None)
            search_text = request.GET.get('search_text', None)
            is_quick_sale = request.GET.get('is_quick_sale', None)
            checkout_id = request.GET.get('checkout_id', None)
            
            sale_record = matching_records(location= location,
                                            range_start = range_start,
                                            range_end = range_end,
                                            client = client,
                                            services = service,
                                            search_text = search_text,
                                            is_quick_sale = is_quick_sale
                                        )
            
            #Apply Pagination
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(sale_record, request)
            serializer = SaleRecordSerializer(result_page, many=True)
            response = {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'current_page': paginator.page.number,
                'per_page': self.page_size,
                'total_pages': paginator.page.paginator.num_pages,
                'success': True,
                'status_code': 200,
                'response': {
                            'message': 'Record fetched successfully!',
                            'error_message': None,
                            'sales': serializer.data,
                            # 'checkout': SaleRecordSerializer(sale_record, many = True).data,
                            # 'coupon': CouponSerializer(coupon_serializer.instance).data,
                            # 'invoice': InvoiceSerializer(invoice).data
                        }
            }
            return Response(response)
        except Exception as e:
            return Response({'error' : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def post(self, request, *args, **kwargs):
        try:
            
            user = request.user
            request.data['user'] = user.id
            # return Response({'user': request.data})
            location_id = request.data['location']
            client = request.data.get('client', None)
            sub_total = request.data['sub_total']
            # validity = request.data['gift_cards_records']
            # validity.get('valid_till'
            # return Response({'data': validity})
            serializer = SaleRecordSerializer(data=request.data, context = {'request': request})
            if serializer.is_valid():
                sale_record = serializer.save()
                try :
                    loyalty_points = sale_record.applied_loyalty_points_records.all()
                    invoice = SaleInvoice.objects.create(
                        user=user,
                        client=sale_record.client,
                        location=sale_record.location,
                        payment_type=request.data.get('payment_type', None),
                        invoice_type='order',
                        checkout_type=f'{request.data.get("checkout_type")}' if request.data.get("checkout_type") else 'sale',
                        sub_total=sale_record.sub_total,
                        total_amount=sale_record.total_price,
                        total_tax=sale_record.total_tax,
                        total_tip=sale_record.total_tip,
                        checkout=sale_record.id,
                    )
                    invoice.save()
                    
                    # return Response({'membership records': membership_order})
                    # if client:
                    # # """
                    # # Sending order details to client through email
                    # # """
                    #     if sale_record.membership_records:
                    #         send_membership_order_email(sale_record.membership_records, location_id, request)
                    #     else:
                    #         send_order_email(sale_record, request)
                        
                    loyalty_points_update(location=location_id, client=client, loyalty_points=loyalty_points, sub_total=sub_total, invoice=invoice)
                except Exception as e:
                    return Response({'error':str(e), 'second': 'Second Try'})
                
                
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
            return Response({"error": str(e), 'First Try':'Error in first Try'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

@api_view(['GET'])
def single_sale_record(request):
    location = request.GET.get('location')
    checkout_id = request.GET.get('checkout_id')
    
    # invoicce translation data
    business_address = BusinessAddress.objects.get(id=location)
    invoice_translations = BusinessAddressSerilaizer(business_address).data
    
    sale_record = SaleRecords.objects.get(id = checkout_id , location= location)
    serializer = SaleRecordSerializer(sale_record).data
    
    response = {
                'success': True,
                'status_code': 200,
                'response': {
                            'message': 'Record fetched successfully!',
                            'error_message': None,
                            'sales': serializer,
                            'invoice_translation': invoice_translations
                        }
            }
    return Response(response)