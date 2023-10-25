
from Product.models import Product

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.views import APIView

from django.db.models import F, Sum, Q
from django.db.models.functions import Coalesce
from Business.models import BusinessAddress
import re

from datetime import datetime, timedelta

DATE_REGEX = '\d{4}-\d{2}-\d{2}'

class FilteredInsightProducts(APIView):
    permission_classes = [AllowAny]

    def __init__(self):
        self.location = None
        self.beggining_date = '2000-01-01'
        self.today_date = datetime.now()
        self.today_date_format = (self.today_date + timedelta(days=1)).strftime('%Y-%m-%d')
        self.days_before_7 = (self.today_date - timedelta(days=7)).strftime('%Y-%m-%d')
        self.days_before_30 = (self.today_date - timedelta(days=30)).strftime('%Y-%m-%d')

        self.queries = {
            'filter' : {},'order_by' : [], 'annotate' : {}
        }

    def retreive_top_sold_query(self, request):
        self.top_sold = request.GET.get('top_sold', None)
        TOP_SOLD_CHOICES = {'TOP_SOLD_PRODUCTS' : self.beggining_date, 'LAST_7_DAYS' : self.days_before_7 , 'LAST_30_DAYS' : self.days_before_30 }

        if self.top_sold :
            self.queries['order_by'].append('-top_sold_orders')
            self.queries['annotate']['top_sold_orders'] = Sum('product_orders__quantity')
            if self.top_sold in TOP_SOLD_CHOICES or re.match(DATE_REGEX, self.top_sold):
                # if self.top_sold != 'TOP_SOLD_PRODUCTS':
                value = self.top_sold
                if value in ['LAST_7_DAYS', 'LAST_30_DAYS', 'TOP_SOLD_PRODUCTS']:
                    value = TOP_SOLD_CHOICES.get(value)
                    self.queries['filter']['product_orders__created_at__range'] = (value, self.today_date_format)
                else:
                    self.queries['filter']['product_orders__created_at__date'] = value

                self.queries['filter']['product_orders__location__id'] = self.location
            else:
                return Response(
                    {
                        'status' : False,
                        'status_code' : 400,
                        'response' : {
                            'message' : 'Invalid Top Sold Query',
                            'error_message' : None,
                        }
                    },
                    status=status.HTTP_200_OK
                )
            
    def retreive_most_consumed_query(self, request):
        self.most_consumed = request.GET.get('most_consumed', None)
        MOST_CONSUMED_CHOICES = {'MOST_COMSUMED_PRODUCTS' : self.beggining_date, 'LAST_7_DAYS' : self.days_before_7 , 'LAST_30_DAYS' : self.days_before_30 }

        if self.most_consumed :
            self.queries['order_by'].append('-most_consumed_products')
            self.queries['annotate']['most_consumed_products'] = Sum('consumptions__quantity')
            if self.most_consumed in MOST_CONSUMED_CHOICES or re.match(DATE_REGEX, self.most_consumed):
                # if self.most_consumed != 'MOST_CONSUMED_PRODUCTS':
                value = self.most_consumed
                if value in ['LAST_7_DAYS', 'LAST_30_DAYS', 'MOST_COMSUMED_PRODUCTS']:
                    value = MOST_CONSUMED_CHOICES.get(value)
                    self.queries['filter']['consumptions__created_at__range'] = (value, self.today_date_format)
                else:
                    self.queries['filter']['consumptions__created_at__date'] = value

                self.queries['filter']['consumptions__location__id'] = self.location
            else:

                return Response(
                    {
                        'status' : False,
                        'status_code' : 400,
                        'response' : {
                            'message' : 'Invalid Top Sold Query',
                            'error_message' : None,
                        }
                    },
                    status=status.HTTP_200_OK
                )
            
    def retreive_most_ordered_query(self, request):
        # string mapping
        self.most_ordered = request.GET.get('most_ordered', None) 

        # date ranges
        self.is_date_most_ordered = request.GET.get('is_date_most_ordered', None)
        self.start_date = request.GET.get('startDate', None)
        self.end_date = request.GET.get('endDate', None)

        # self.queries['order_by'].append('-most_ordered_products')
        # self.queries['annotate']['most_ordered_products'] = Sum('product_order_stock__rec_quantity')
        # self.queries['filter']['product_order_stock__order__to_location__id'] = self.location

        if self.most_ordered :
            MOST_ORDERED_CHOICES = {'MOST_ORDERED_PRODUCTS' : self.beggining_date, 'LAST_7_DAYS' : self.days_before_7 , 'LAST_30_DAYS' : self.days_before_30 }
            if self.most_ordered in MOST_ORDERED_CHOICES or re.match(DATE_REGEX, self.most_ordered):
                value = self.most_ordered
                if value in ['LAST_7_DAYS', 'LAST_30_DAYS', 'MOST_ORDERED_PRODUCTS']:
                    value = MOST_ORDERED_CHOICES.get(value)
                    self.queries['filter']['product_order_stock__order__created_at__range'] = (value, self.today_date_format)
                    self.queries['order_by'].append('-most_ordered_products')
                    self.queries['annotate']['most_ordered_products'] = Sum('product_order_stock__rec_quantity')
                    self.queries['filter']['product_order_stock__order__to_location__id'] = self.location
        elif self.is_date_most_ordered and self.start_date and self.end_date:
            self.queries['order_by'].append('-most_ordered_products')
            self.queries['annotate']['most_ordered_products'] = Sum('product_order_stock__rec_quantity')
            self.queries['filter']['product_order_stock__order__to_location__id'] = self.location
            self.queries['filter']['product_order_stock__order__created_at__range'] = (self.start_date, self.end_date)
        else:
            return Response(
                {
                    'status' : False,
                    'status_code' : 400,
                    'response' : {
                        'message' : 'Invalid Top Sold Query',
                        'error_message' : None,
                    }
                },
                status=status.HTTP_200_OK
            )
            
    def retreive_most_transferred_query(self, request):
        self.most_transferred = request.GET.get('most_transferred', None)


        if self.most_transferred :
            MOST_TRANSFERRED_CHOICES = {'MOST_TRANSFERRED_PRODUCTS' : self.beggining_date, 'LAST_7_DAYS' : self.days_before_7 , 'LAST_30_DAYS' : self.days_before_30 }
            self.queries['order_by'].append('-most_transferred_products')
            self.queries['annotate']['most_transferred_products'] = Sum('products_stock_transfers__quantity')
            if self.most_transferred in MOST_TRANSFERRED_CHOICES or re.match(DATE_REGEX, self.most_transferred):
                # if self.most_transferred != 'MOST_TRANSFERRED_PRODUCTS':
                value = self.most_transferred
                if value in ['LAST_7_DAYS', 'LAST_30_DAYS', 'MOST_TRANSFERRED_PRODUCTS']:
                    value = MOST_TRANSFERRED_CHOICES.get(value)
                    self.queries['filter']['products_stock_transfers__created_at__range'] = (value, self.today_date_format)
                else:
                    self.queries['filter']['products_stock_transfers__created_at__date'] = value

                self.queries['filter']['products_stock_transfers__from_location__id'] = self.location
            else:
                return Response(
                    {
                        'status' : False,
                        'status_code' : 400,
                        'response' : {
                            'message' : 'Invalid Top Sold Query',
                            'error_message' : None,
                        }
                    },
                    status=status.HTTP_200_OK
                )
    
    def retreive_low_stock_products_query(self, request):
        self.low_stock_products = request.GET.get('low_stock_products', None)

        if self.low_stock_products:
            self.queries['annotate']['sum_of_total_available_stock'] = Sum('product_stock__available_quantity')
            self.queries['annotate']['sum_of_total_lowest_stock_amount'] = Sum('product_stock__low_stock')
            self.queries['annotate']['remaing_stock'] = F('sum_of_total_available_stock') - F('sum_of_total_lowest_stock_amount')

            self.queries['filter']['sum_of_total_available_stock__lte'] = F('sum_of_total_lowest_stock_amount')


    def retreive_out_of_stock_products_query(self, request):
        self.out_of_stock_products = request.GET.get('out_of_stock_products', None)

        if self.out_of_stock_products:

            self.queries['filter']['product_stock__available_quantity__lte'] = 0


    def get_date_object(self, string_date: str):
        """
        string_time: A date in string format to get the time object
        e.g: 2023-10-03
        """
        return datetime.strptime(string_date, '%Y-%m-%d')



    def get(self, request):
        self.queries = {
            'filter' : {},'order_by' : [], 'annotate' : {}
        }
        self.queries['filter'] = {}
        self.queries['annotate'] = {}
        self.queries['order_by'] = []

        location_id = request.GET.get('location', None)

        if not location_id:
            return Response(
                {
                    'status' : False,
                    'status_code' : 400,
                    'response' : {
                        'message' : 'Please provide following missing fields',
                        'error_message' : 'Missing fields error',
                        'fields' : [
                            'location'
                        ]
                    }
                },
                status=status.HTTP_200_OK
            )
        
        self.location = location_id

        response = self.retreive_top_sold_query(request)
        if response is not None:
            return response
        response = self.retreive_most_consumed_query(request)
        if response is not None:
            return response
        response = self.retreive_most_ordered_query(request)
        if response is not None:
            return response
        response = self.retreive_most_transferred_query(request)
        if response is not None:
            return response
        # response = self.retreive_low_stock_products_query(request)
        # if response is not None:
        #     return response
        # response = self.retreive_out_of_stock_products_query(request)
        # if response is not None:
        #     return response

        filtered_products = Product.objects.filter(
            is_deleted = False,
            product_stock__location__id = location_id,
            **self.queries['filter'],
        ).annotate(
            **self.queries['annotate'],
        ).distinct().order_by(*self.queries['order_by'])

        # serialized = ProductInsightSerializer(filtered_products, many=True)

        data = []

        for product_instance in filtered_products:
            product = {
                'id' : f'{product_instance.short_id}',
                'name' : f'{product_instance.name}',
                'product_type' : f'{product_instance.product_type}',
                'brand_name' : f'{product_instance.brand.name}' if product_instance.brand else '-------',
                'category_name' : f'{product_instance.category.name}' if product_instance.category else '-------',
            }

            if self.top_sold and (product_instance.top_sold_orders or product_instance.top_sold_orders == 0):
                product['top_sold_orders'] = int(product_instance.top_sold_orders)
                product['quantity'] = int(product_instance.top_sold_orders)
            else:
                product['top_sold_orders'] = self.top_sold


            if self.most_consumed and (product_instance.most_consumed_products or product_instance.most_consumed_products == 0):
                product['most_consumed_products'] = int(product_instance.most_consumed_products)
                product['quantity'] = int(product_instance.most_consumed_products)
            else:
                product['most_consumed_products'] = self.most_consumed

            if self.most_ordered and (product_instance.most_ordered_products or product_instance.most_ordered_products == 0):
                product['most_ordered_products'] = int(product_instance.most_ordered_products)
                product['quantity'] = int(product_instance.most_ordered_products)
            else:
                product['most_ordered_products'] = self.most_ordered

            if self.most_transferred and (product_instance.most_transferred_products or product_instance.most_transferred_products == 0):
                product['most_transferred_products'] = int(product_instance.most_transferred_products)
                product['quantity'] = int(product_instance.most_transferred_products)
            else:
                product['most_transferred_products'] = self.most_transferred


            # if self.low_stock_products :
            #     if product_instance.sum_of_total_available_stock:
            #         product['sum_of_total_available_stock'] = int(product_instance.sum_of_total_available_stock)
            #     if product_instance.sum_of_total_lowest_stock_amount:
            #         product['sum_of_total_lowest_stock_amount'] = int(product_instance.sum_of_total_lowest_stock_amount)
            #     if product_instance.remaing_stock:
            #         product['lowest_stock'] = int(product_instance.remaing_stock)

            # if self.out_of_stock_products:
            #     product['available_stock'] = int(product_instance.product_stock.all().available_quantity)

            data.append(product)

        self.top_sold = None
        self.most_consumed = None
        self.most_transferred = None
        self.low_stock_products = None
        self.out_of_stock_products = None
        self.most_ordered = None
        self.today_date = None
        self.today_date_format = None
        self.days_before_7 = None
        self.days_before_30 = None
        query_copy = self.queries
        
        self.queries = {
            'filter' : {},'order_by' : [], 'annotate' : {}
        }
        response = Response(
            {
                'status' : True,
                'status_code' : 200,
                'request' : {
                    'queries' : str(query_copy)
                },
                'response' : {
                    'message' : 'Insight Products',
                    'error_message' : None,
                    'products' : data
                }
            },
            status=status.HTTP_200_OK
        )
        return response
    


@api_view(['GET'])
@permission_classes([AllowAny])
def get_filtered_chat_products(request):
    location_id = request.GET.get('location', None)
    selected_year = request.GET.get('selected_year', '2023')

    if not location_id:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'response' : {
                    'message' : 'Please provide following missing fields',
                    'error_message' : 'Missing fields error',
                    'fields' : [
                        'location'
                    ]
                }
            },
            status=status.HTTP_200_OK
        )
    location_obj = BusinessAddress.objects.get(id=location_id)
    # products = Product.objects.annotate(
    #     most_transferred_products = Sum('products_stock_transfers__quantity')
    # ).filter(
    #     product_stock__location__id = location_id,
    #     is_deleted = False,
    #     products_stock_transfers__created_at__range = ('2020-01-01', f'{selected_year}-12-31')
    # ).order_by('-most_transferred_products')[:10]

    sum_filter = Q(product_orders__location=location_obj)
    products = Product.objects \
    .filter(
        product_stock__location = location_obj,
        is_deleted = False,
        product_orders__created_at__range = ('2020-01-01', f'{selected_year}-12-31'),
        product_orders__location=location_obj) \
    .annotate(
        most_transferred_products = Coalesce(Sum('product_orders__quantity', filter=sum_filter), 0) \
    ).order_by('-most_transferred_products')[:10]


    data = []
    for product_instance in products:
        product = {
            # 'id' : f'{product_instance.id}',
            'key' : f'{product_instance.name}',
            'data' : int(product_instance.most_transferred_products),
        }

        data.append(product)


    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Insight Products',
                    'error_message' : None,
                    'products' : data
                }
            },
            status=status.HTTP_200_OK
        )