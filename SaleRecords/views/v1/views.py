
from Invoices.models import SaleInvoice

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.db.models import Sum, Avg
from django.db.models import Q
from django.db.models import Value

from SaleRecords.helpers import matching_records, loyalty_points_calculations
from Client.Constants.client_order_email import send_order_email, send_membership_order_email
from Reports.models import DiscountPromotionSalesReport

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
            # search_text = request.GET.get('search_text', None)
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
            client_type = request.data['client_type']
            loyalty_points_data = request.data.get('applied_loyalty_points_records', [])
            applied_promotions = request.data.get('applied_promotions_records',[])
            
            serializer = SaleRecordSerializer(data=request.data, context = {'request': request})
            if serializer.is_valid():
                sale_record = serializer.save()
                try :
                
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
                    # raise ValidationError('Coming here')
                    # loyalty_points_calculations(location=location_id, client=client, loyalty_points=loyalty_points, sale_record=sale_record, sub_total=sub_total, invoice=invoice)
                    if client_type == 'In_Saloon':
                        logs_points_redeemed = 0
                        logs_total_redeened_value = 0
                        # raise ValidationError(f'{sale_record.applied_loyalty_points_records}')
                        
                        try:
                            
                            if len(loyalty_points_data) > 0:
                                # loyalty_points_record = loyalty_points_data[0]
                                loyalty_points_record = loyalty_points_data[0]
                                loyalty_points = ClientLoyaltyPoint.objects.get(id = loyalty_points_record.get('client_loyalty_point'))
                                # raise ValidationError('If part')
                                if loyalty_points:
                                    client_points = ClientLoyaltyPoint.objects.get(id = loyalty_points_record.get('client_loyalty_point'))
                                    
                                    client_points.points_redeemed = float(client_points.points_redeemed) + float(loyalty_points_record.get('redeemed_points'))
                                    client_points.save()

                                    single_point_value = client_points.customer_will_get_amount / client_points.for_every_points
                                    total_redeened_value = float(single_point_value) * float(loyalty_points_record.get('redeemed_points'))

                                    logs_points_redeemed = loyalty_points_record.get('redeemed_points')
                                    logs_total_redeened_value = total_redeened_value
                        except Exception as e:
                            return Response({'error':str(e), 'loyalty Point cal':"error in loyalty points cal"})
                            
                        else:
                            # raise ValidationError('Coming in the else part')
                            try:
                                
                                allowed_points = LoyaltyPoints.objects.filter(
                                                            Q(loyaltytype='Service') |
                                                            Q(loyaltytype='Both'),
                                                            location=request.data.get('location'),
                                                            # amount_spend = total_price,
                                                            is_active=True,
                                                            is_deleted=False
                                                        )
                                
                                if len(allowed_points) > 0:
                                    point = allowed_points[0]
                                    client_points, created = ClientLoyaltyPoint.objects.get_or_create(
                                        location_id=location_id,
                                        client=sale_record.client,
                                        loyalty_points=point, # loyalty Foreignkey
                                    )

                                    loyalty_spend_amount = point.amount_spend
                                    loyalty_earned_points = point.number_points  # total earned points if user spend amount point.amount_spend

                                    # gained points based on customer's total Checkout Bill

                                    earned_points = (float(sub_total) / float(loyalty_spend_amount)) * float(loyalty_earned_points)
                                    earned_amount = (earned_points / point.earn_points) * float(point.total_earn_from_points)

                                    if created:
                                        client_points.total_earn = earned_points
                                        client_points.total_amount = earned_amount

                                    else:
                                        client_points.total_earn = float(client_points.total_earn) + float(earned_points)
                                        client_points.total_amount = client_points.total_amount + float(earned_amount)

                                    client_points.for_every_points = point.earn_points
                                    client_points.customer_will_get_amount = point.total_earn_from_points

                                    client_points.save()

                                    LoyaltyPointLogs.objects.create(
                                        location_id=location_id,
                                        client=client_points.client,
                                        client_points=client_points,
                                        loyalty=point,
                                        points_earned=earned_points,
                                        points_redeemed=logs_points_redeemed,
                                        balance=client_points.total_available_points,
                                        actual_sale_value_redeemed=logs_total_redeened_value,
                                        invoice=invoice.id,
                                        checkout=sale_record.id
                                    )
                            except Exception as e:
                                return Response({"error": str(e), "error occured": "loyalty else part"})
                    try:     
                        if len(applied_promotions) > 0:
                            promotion_data = applied_promotions[0]
                            DiscountPromotionSalesReport.objects.create(
                                    checkout_id=sale_record.id,
                                    checkout_type='Sale',
                                    invoice=invoice,
                                    promotion_id=promotion_data.get('promotion'),
                                    promotion_type= promotion_data.get('promotion_type'),
                                    user=user,
                                    client_id=client,
                                    location_id=location_id,
                                )
                    except Exception as e:
                        return Response({'error':str(e), 'error occured':'error occured in applied promotion'})
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

# Get Sales Analytics For POS Analytics ------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def get_sales_analytics(request):
    location_id = request.GET.get('location_id', None)
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)
    today = request.GET.get('today', None)
    
    query = Q()
    location = Q()
    business= Q()
    
    try:    
        if location_id:
            location &= Q(location=location_id)
            business &= Q(business_address=location_id)
            
        if year:
            query &= Q(created_at__year=year)
        
        if month:
            query &= Q(created_at__month=month)
        
        if today:
            query &= Q(created_at__date=today)
            
        # Get Target Data    
        service_target = ServiceTarget.objects.filter(query, location) \
                            .aggregate(total_service_target=Coalesce(Sum('service_target', output_field=FloatField()), Value(0, output_field=FloatField())))
        retail_target = RetailTarget.objects.filter(query, location) \
                            .aggregate(total_retail_target=Coalesce(Sum('brand_target', output_field=FloatField()), Value(0, output_field=FloatField())))
        
        # Get Sale Records
        service = SaleRecordServices.objects.filter(query).aggregate(total_service_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        product = SaleRecordsProducts.objects.filter(query).aggregate(total_product_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        vouchers = SaleRecordVouchers.objects.filter(query).aggregate(total_vouchers_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        membership = SaleRecordMembership.objects.filter(query).aggregate(total_membership_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        gift_card = PurchasedGiftCards.objects.filter(query).aggregate(total_gift_card_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        
        appointment_average = SaleRecordsAppointmentServices.objects.filter(query) \
                                .aggregate(avg_appointment=Coalesce(Avg('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        
        # Appointment Count
        cancel_appointment = Appointment.objects.filter(business, query, status='Cancelled').count()
        if location_id:
            location=Q(sale_record__location__id=location_id)
        finished_appointment = SaleRecordsAppointmentServices.objects.filter(location, appointment_status__in=['Paid', 'Done']).count()
        
        # Total Appointment count
        total_appointment = cancel_appointment + finished_appointment
        
        # Calculate the total sum
        total_sale = (
            service['total_service_sale'] +
            product['total_product_sale'] +
            vouchers['total_vouchers_sale'] +
            membership['total_membership_sale'] +
            gift_card['total_gift_card_sale']
        )
        avg_sale = total_sale / 5 # average of 5 sales records
        
        data = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Data fetched successfully',
            'error_message': None,
            'data': {
                'sales_cards':{
                    'avg_sale': avg_sale,
                    'appointment_average': appointment_average['avg_appointment'],
                },
                'sales_progress': {
                    'service': {
                        'total_service_target': service_target['total_service_target'],
                        'service_total_sale': service['total_service_sale'],
                    },
                    'product': {
                        'total_retail_target': retail_target['total_retail_target'],
                        'product_total_sale': product['total_product_sale'],
                    },
                    'vouchers_total_sale': vouchers['total_vouchers_sale'],
                    'membership_total_sale': membership['total_membership_sale'],
                    'gift_card_total_sale': gift_card['total_gift_card_sale'],
                    'total_sale': total_sale,
                },
                'appointment_progress': {
                    'cancel_appointment': cancel_appointment,
                    'finished_appointment': finished_appointment,
                    'total_appointment': total_appointment,
                }
            }   
        }
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle exceptions and return an appropriate error response
        error_data = {
            'success': False,
            'status_code': 400,
            'message': 'Internal Server Error',
            'error_message': str(e),
            'data': None
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
