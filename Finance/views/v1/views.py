from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from Utility.Campaign import send_refund_email

from Finance.models import Refund, RefundCoupon, AllowRefunds,AllowRefundPermissionsEmployees, RefundProduct, RefundServices
from Finance.serializers import RefundSerializer, RefundCouponSerializer, AllowRefundsSerializer, RefundProductSerializer , RefundServiceSerializer
from Finance.helpers import short_uuid, check_permission, check_days
from SaleRecords.models import SaleRecordsAppointmentServices, SaleRecordsProducts, SaleRecordServices
from Invoices.models import SaleInvoice
from Client.serializers import SaleInvoiceSerializer
from Client.models import Client
from Service.models import ServiceGroup


from Appointment.models import AppointmentCheckout, AppointmentService
from Order.models import Checkout, ProductOrder, ServiceOrder


from django.core.exceptions import ObjectDoesNotExist









@api_view(['GET'])
def check_permission_view(request):
    try:
        invoice_id = request.query_params.get('invoice_id')
        location = request.query_params.get('location')
        user = request.user.id
        if check_days(invoice_id, location) or check_permission(user, location, invoice_id):
            response_data = {
                    'success': True,
                    'status_code': 201,
                    'response': {
                        'message': 'Permission granted!',
                        'error_message': None,
                        'check_days_response': check_days(invoice_id, location),
                        'check_permission': check_permission(user, location, invoice_id),
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
                'check_days_response': check_days(invoice_id, location),
                'check_permission': check_permission(user, location, invoice_id),
                'data': []
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'erorr': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class RefundAPIView(APIView):
    pagination_class = PageNumberPagination
    page_size = 10
    def get(self, request, *args, **kwargs):
        location_id = request.GET.get('location_id', None)
        search_txt = request.GET.get('search_text', None)
        service_group = request.GET.get('service_group', None)
        brand_id = request.GET.get('brand_id', None)
        
        query = Q()
        if location_id:
            query &= Q(refund__location=location_id)
            
        if search_txt:
            query &= Q(refund__client__full_name__icontains=search_txt) | Q(product__name__icontains=search_txt)
            
        if brand_id:
            query &= Q(product__brand_id=brand_id)
            
        if request.GET.get('type') == 'Product':
            refunds = RefundProduct.objects.filter(query).order_by('-created_at')
            
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(refunds, request)
            refund_serializer = RefundProductSerializer(result_page, many=True)
            if not refunds:
                response_data = {
                    'success': False,
                    'status_code': 400,
                    'response': {
                        'message': 'No Records found',
                        'error_message': None,
                        'data': None
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
            response_data = {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'current_page': paginator.page.number,
                'per_page': self.page_size,
                'total_pages': paginator.page.paginator.num_pages,
                'success': True,
                'status_code': 200,
                'response': {
                    'message': 'Record fetched successfully',
                    'error_message': None,
                    'data': {
                        'refund_data': refund_serializer.data,
                    }
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        query = Q()
        if service_group:
            services =ServiceGroup.objects.get(id=service_group).services.all()
            services_list = list(services.values_list('id', flat=True))
            query &= Q(service__in=services_list)
            
        if request.GET.get('type') == 'Service':
            refunds = RefundServices.objects.filter(query).order_by('-created_at')
            
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(refunds, request)
            refund_serializer = RefundServiceSerializer(result_page, many=True)
            if not refunds:
                response_data = {
                    'success': False,
                    'status_code': 400,
                    'response': {
                        'message': 'No Records found',
                        'error_message': None,
                        'data': None
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
            response_data = {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'current_page': paginator.page.number,
                'per_page': self.page_size,
                'total_pages': paginator.page.paginator.num_pages,
                'success': True,
                'status_code': 200,
                'response': {
                    'message': 'Record fetched successfully',
                    'error_message': None,
                    'data': {
                        'refund_data': refund_serializer.data,
                    }
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
            


    def post(self, request, *args, **kwargs):  # sourcery skip: extract-method
        '''
    POST REQUEST FOR THE REFUND
    Payload formate:
            {
                "business": "c2ee68e4-e30a-43c5-ba55-b09aca4f50b7",
                "refund_invoice_id": "83d777d8-7790-4cc8-adf2-5ac2042407f9",
                "client": "26bd481e-613a-4f55-89ac-b09c5f003b5d",
                "location": "73f662bd-9720-4af7-bcef-6aec2888d1de",
                "client_type": "In_Saloon",
                "payment_type": "Cash",
                "service_commission_type": "",
                "product_commission_type": "",
                "voucher_commission_type": "",
                "checkout": "0e60c8f2-7064-4307-aa8d-cdb674bebf52",
                "checkout_type": "sale",
                "refunded_products": [
                    {
                    "product": "1014d168-b507-4b2b-bc40-ccdb72baaefa",
                    "refunded_quantity": 1,
                    "refunded_amount": 185
                    },

                    {
                    "product": "3a540536-cc09-4b04-a542-3f288a5b925e",
                    "refunded_quantity": 2,
                    "refunded_amount": 666
                    },
                    {
                    "product": "49e6607a-849c-498b-b5f2-0b7e7f625faf",
                    "refunded_amount": 200,
                    "refunded_quantity": 2
                    }
                ],
                "refunded_services": [],
                "refund_type": "credit_refund",
                "expiry_date": "2024-01-05",
                "total_refund_amount": 1051
                
            }


            '''
            
            
        refund_invoice_id = request.data.get('refund_invoice_id')
        refund_price = request.data.get('total_refund_amount')
        payment_type = request.data.get('payment_type')
        client = request.data.get('client')
        checkout_type = request.data.get('checkout_type') # appointment or sale
        expiry_date = request.data.get('expiry_date')
        
        try:
            user = request.user
            request.data['user'] = user.id
            expiry_date = request.data.get('expiry_date')
        
            serializer = RefundSerializer(data=request.data, context={'request': request})
            # return Response({'data': serializer.validated_data}, status=status.HTTP_200_OK)
            if serializer.is_valid():
                # return Response({'data': serializer.initial_data}, status=status.HTTP_200_OK)
                refund_instance = serializer.save()
                
                
                # refunded_products_ids = list(refundprodcts.objects.filter().values_list('id', flat=True))
                refunded_products_ids = refund_instance.refunded_products.values_list('product__id', flat=True)
                refunded_services_ids = refund_instance.refunded_services.values_list('service__id', flat=True)
                # return Response({'refund services count': refunded_services_ids.count(), 'refund product count': refunded_products_ids })
                # return Response({'refund product list': refunded_products_ids, 'refund service list': refunded_services_ids})
                #      create invoice
                try:    
                    invoice = SaleInvoice.objects.get(id=refund_invoice_id) 
                    checkout_instance = invoice.checkout_instance 
                    checkout_instance.is_refund = True
                    checkout_instance.save() 
                    newCheckoutInstance = checkout_instance  
                    newCheckoutInstance.pk = None 
                    newCheckoutInstance.is_refund = True
                    newCheckoutInstance.save()
                    newCheckoutInstance.checkout_type = 'Refund'
                    newCheckoutInstance.is_refund = True
                    newCheckoutInstance.sub_total = float(-refund_price)
                    newCheckoutInstance.total_price = float(-refund_price)
                    newCheckoutInstance.save()

                    if checkout_type == 'Appointment': 
                        print('coming here')
                        appointment_services  = SaleRecordsAppointmentServices.objects.get(sale_record = checkout_instance)
                        # raise ValueError(f'Coming here {appointment_services.count()}')
                        newAppointment = appointment_services.appointment
                        newAppointment.pk = None 
                        newAppointment.save() 
                        
                        order_items = SaleRecordsAppointmentServices.objects.filter(appointment = appointment_services.appointment, service__id__in = refunded_services_ids) 
                        # return Response({'Appointment order count ': order_items.count() })
                        # for order in order_items:
                        #     order.pk = None
                        #     order.is_refund = 'refund'
                        #     order.price = float(-RefundServices.objects.get(service__id = order.id).refunded_amount)
                        #     # order.tip = 0
                        #     # order.gst = 0
                        #     # order.tax_amount = 0
                        #     order.appointment = newAppointment
                        #     order.save()
                        
                        
                        for order in order_items:
                            refunded_services = RefundServices.objects.get(checkouts = invoice.checkout_instance.id,service = order.service)
                            
                            SaleRecordsAppointmentServices.objects.create(
                                sale_record = newCheckoutInstance,
                                appointment = newAppointment,
                                employee = order.employee, 
                                service = order.service,
                                service_start_time = order.service_start_time,
                                service_end_time = order.service_end_time,
                                quantity = 1,
                                price = float(-refunded_services.refunded_amount)
                            )
                    
                        # or you can do it in loop
                    else: 
                        product_orders = SaleRecordsProducts.objects.filter(sale_record=invoice.checkout_instance, product__id__in = refunded_products_ids) 
                        # return Response({'product orders count': product_orders.count()})

                        for order in product_orders:
                                # raise ValueError('comming here')
                                refund_product = RefundProduct.objects.get(checkouts = invoice.checkout_instance.id,product__id=order.product.id)
                                # raise ValueError('comign here')
                                
                                
                                SaleRecordsProducts.objects.create(
                                    sale_record= newCheckoutInstance,
                                    employee=order.employee,  
                                    product=order.product,
                                    quantity = refund_product.refunded_quantity,
                                    price = float(-refund_product.refunded_amount),
                                )
                                
                            
                            
                        service_orders = SaleRecordServices.objects.filter(sale_record=invoice.checkout_instance, service__id__in = refunded_services_ids) 
                        # service_orders.update(pk = None, checkout=newCheckoutInstance) 
                        for order in service_orders:
                            
                                refunded_services = RefundServices.objects.get(checkouts = invoice.checkout_instance.id,service__id = order.service.id)
                                SaleRecordServices.objects.create(
                                    sale_record = newCheckoutInstance,
                                    employee = order.employee,
                                    service = order.service,
                                    quantity = 1,
                                    price = float(-refunded_services.refunded_amount)
                                )
                            
                            
                        
                    # newInvoice = invoice 
                    # newInvoice.pk = None 
                    # newInvoice.invoice_type = 'refund'
                    # newInvoice.payment_type = 'Cash'
                    # newInvoice.client_type = 'Walk_in'
                    # newInvoice.sub_total = float(-refund_price)
                    # newInvoice.total_amount = float(-refund_price)
                    # newInvoice.checkout = str(newCheckoutInstance.id) 
                    # newInvoice.total_tax = 0
                    # newInvoice.total_tip = 0
                    # # newInvoice.checkout_type = 'refund'
                    # newInvoice.payment_type = payment_type
                    # newInvoice.save() 
                    invoice = SaleInvoice.objects.create(
                        user=user,
                        client=invoice.client,
                        location=invoice.location,
                        payment_type=payment_type,
                        invoice_type='refund',
                        change=0,
                        checkout_type='refund',
                        sub_total=float(-refund_price),
                        total_amount=float(-refund_price),
                        total_tax=0,
                        total_tip=0,
                        checkout=newCheckoutInstance.id,
                    )
                    invoice.save()

                    try:
                        client_instance = Client.objects.get(id=client)
                        client_email = client_instance.email
                    except Client.DoesNotExist:
                        # Handle the case where the client does not exist
                        client_email = None  # or any default value or appropriate handling
                        
                    #send email to client running on thread
                    send_refund_email(client_email=client_email)  
                    
                except Exception as e:
                        return Response({'Error': str(e), 'error':'Second Try'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                if expiry_date:
                    coupon_data = {
                        'user': request.user.id,
                        'client': client,
                        'coupon_type': 'refund',
                        'checkout_id': str(newCheckoutInstance.id),
                        'refund_coupon_code': f"{short_uuid(refund_instance.id)}",
                        'amount': refund_instance.total_refund_amount,
                        'expiry_date': expiry_date,
                        'related_refund': refund_instance.id,
                    }
                    try:
                        coupon_serializer = RefundCouponSerializer(data=coupon_data)
                        coupon_serializer.is_valid(raise_exception=True)
                        coupon_serializer.save()
                    except Exception as e:
                        return Response({'Error': str(e),'error': 'Third Try'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    response_data = {
                        'success': True,
                        'status_code': 201,
                        'response': {
                            'message': 'Refund created successfully',
                            'error_message': None,
                            'data': {
                                'refund': RefundSerializer(serializer.instance).data,
                                # 'coupon': CouponSerializer(coupon_serializer.instance).data,
                                'invoice': SaleInvoiceSerializer(invoice).data
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
                                'invoice': SaleInvoiceSerializer(invoice).data, 
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
            return Response({"error": str(e), 'error':'First Try'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RefundedCoupons(APIView):
    '''Getting coupons with the refund Data'''

    def get(self, request, *args, **kwargs):
        coupons = RefundCoupon.objects.select_related(
            'related_refund__business', 'related_refund__location').all()
        serializer = RefundCouponSerializer(coupons, many=True)
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
        