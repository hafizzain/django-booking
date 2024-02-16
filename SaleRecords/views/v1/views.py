
from Invoices.models import SaleInvoice

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from django.db.models import Sum, Avg
from django.db.models import Q

from SaleRecords.helpers import matching_records, loyalty_points_calculations
from Client.Constants.client_order_email import send_order_email, send_membership_order_email

from SaleRecords.serializers import *
from Business.serializers.v1_serializers import BusinessAddressSerilaizer
from TragetControl.models import *


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
            serializer = SaleRecordSerializer(result_page, many=True, context = {'request': request})
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
                    # from django.http import JsonResponse
                    # from django.core.serializers import serialize
                    
                    loyalty_points = sale_record.applied_loyalty_points_records
                    
                    # serialized_data = serialize('json', loyalty_points)

                    # Return the serialized data as JSON response
                    # return JsonResponse(serialized_data, safe=False)
                
                
                
                    invoice = SaleInvoice.objects.create(
                        user=user,
                        client=sale_record.client,
                        location=sale_record.location,
                        payment_type=request.data.get('payment_type', None),
                        invoice_type='order',
                        change = request.data.get('change', 0),
                        checkout_type=f'{request.data.get("checkout_type")}' if request.data.get("checkout_type") else 'sale',
                        sub_total=sale_record.sub_total,
                        total_amount=sale_record.total_price,
                        total_tax=sale_record.total_tax,
                        total_tip=sale_record.total_tip,
                        checkout=sale_record.id,
                    )
                    invoice.save()
                    
                    # return Response({'membership records': membership_order})
                    if client:
                    # """
                    # Sending order details to client through email
                    # """
                        if sale_record.membership_records:
                            # send_membership_order_email(sale_record.membership_records, location_id, request)
                            pass
                        else:
                            send_order_email(sale_record, request)
                    raise ValidationError('Coming here')
                    # loyalty_points_calculations(location=location_id, client=client, loyalty_points=loyalty_points, sale_record=sale_record, sub_total=sub_total, invoice=invoice)
                except Exception as e:
                    return Response({'error':str(e), 'second': 'Second Try'})
                
                
                response_data = {
                        'success': True,
                        'status_code': 200,
                        'response': {
                            'message': 'Checkout created successfully!',
                            'error_message': None,
                            'data': {
                                'checkout': SaleRecordSerializer(sale_record, context = {'request': request}).data,
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
    serializer = SaleRecordSerializer(sale_record, context = {'request': request}).data
    
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

# Get Sales Analytics Pos Analytics ------------------------------------------------------------------------------------------
@api_view(['GET'])
def get_sales_analytics(request):
    try:
        location_id = request.GET.get('location_id')
        year = request.GET.get('year')
        month = request.GET.get('month')
        today = request.GET.get('today')
        
        query = Q()
        if location_id:
            query &= Q(location=location_id)
            
        if year:
            query &= Q(created_at__year=year)
        
        if month:
            query &= Q(created_at__month=month)
        
        if today:
            query &= Q(created_at__date=today)
            
        # Get Target Data    
        service_target = ServiceTarget.objects.filter(query)
        retail_target = RetailTarget.objects.filter(query).annotate(total_retail_target=Sum('brand_target'))
        
        # Get Sale Records
        service = SaleRecordServices.objects.filter(query).annotate(total_service_sale=Sum('price'))
        product = SaleRecordsProducts.objects.filter(query).annotate(total_product_sale=Sum('price'))
        vouchers = SaleRecordVouchers.objects.filter(query).annotate(total_vouchers_sale=Sum('price'))
        membership = SaleRecordMembership.objects.filter(query).annotate(total_membership_sale=Sum('price'))
        gift_card = PurchasedGiftCards.objects.filter(query).annotate(total_gift_card_sale=Sum('price'))
        
        appointment_average = SaleRecordsAppointmentServices.objects.filter(query).annotate(avg_appointment_sale=Avg('price'))
        
        # Get Total Sales
        total_sum = (
            service.aggregate(total=Sum('total_service_sale'))['total'] or 0 +
            product.aggregate(total=Sum('total_product_sale'))['total'] or 0 +
            vouchers.aggregate(total=Sum('total_vouchers_sale'))['total'] or 0 +
            membership.aggregate(total=Sum('total_membership_sale'))['total'] or 0 +
            gift_card.aggregate(total=Sum('total_gift_card_sale'))['total'] or 0
        )
        
        data = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Data fetched successfully',
            'error_message': None,
            'data': {
                'service_target': ServiceTargetSerializer(service_target, many=True).data,
                'retail_target': RetailTargetSerializer(retail_target, many=True).data,
                'service': ServiceRecordSerializer(service, many=True).data,
                'product': product,
                # 'vouchers': VoucherRecordSerializer(vouchers, many=True).data,
                # 'membership': MembershipRecordSerializer(membership, many=True).data,
                # 'gift_card': GiftCardRecordSerializer(gift_card, many=True).data,
                # 'appointment_average': AppointmentServiceRecordSerializer(appointment_average, many=True).data,
                'total_sum': total_sum
            }
        }
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle exceptions and return an appropriate error response
        error_data = {
            'success': False,
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Internal Server Error',
            'error_message': str(e),
            'data': None
        }
        return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
