import datetime
import json
import csv
from threading import Thread

from django.http import HttpResponse
from django.db.models.functions import Cast
from django.db.models import CharField
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from NStyle.Constants import StatusCodes
from Product.models import ProductTranslations
from Utility.models import Language
from Sale.Constants.Custom_pag import CustomPagination
from Product.Constants.Add_Product import add_product_remaing
from Utility.models import Currency, NstyleFile, ExceptionRecord
from Business.models import Business, BusinessAddress, BusinessVendor
from Product.models import ( Category, Brand, CurrencyRetailPrice , Product, ProductMedia, ProductOrderStockReport, ProductStock
                            , OrderStock, OrderStockProduct, ProductConsumption, ProductStockTransfer
                           )
from Product.serializers import (CategorySerializer, BrandSerializer, ProductSerializer, ProductWithStockSerializer
                                 ,OrderSerializer , OrderProductSerializer, ProductConsumptionSerializer,
                                 ProductStockTransferSerializer, ProductStockReportSerializer
                                 )
from django.db import transaction

import Product.optimized_serializers as optSerializers



@api_view(['GET'])
@permission_classes([AllowAny])
def get_test_api(request):
    product_id = request.data.get('product_id', None)
    from_location_id = request.data.get('from_location_id', None)
    data = []
    location_ids = ['c7dfffd8-f399-48bf-9165-3fe26f565992','340b2c1f-ff66-4327-9cfe-692dff48ca40','8f8b22c9-8410-46b8-b0c7-f520a1480357']
    product = Product.objects.get(id = 'c7dfffd8-f399-48bf-9165-3fe26f565992')#filter(is_deleted = False).exclude(id__in = location_ids)
    data.append(str(product.id))
    product = Product.objects.get(id = '340b2c1f-ff66-4327-9cfe-692dff48ca40')#filter(is_deleted = False).exclude(id__in = location_ids)
    data.append(str(product))
    
    try:
        thrd = Thread(target=add_product_remaing, args=[], kwargs={'product' : product, 'tenant' : request.tenant})
        thrd.start()
    except Exception as err:
        ExceptionRecord.objects.create(
            text=str(err)
        )
    
    data = 'test'
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Service',
                'error_message' : None,
                'service' : data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def export_csv(request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ProductStock.csv"'

        writer = csv.writer(response)
        writer.writerow(['name', 'quantity', 'category', 'product_type'])
        
        for stock in ProductStock.objects.all():
            writer.writerow(
                [
                    stock.product.name,
                    stock.quantity,
                    stock.product.category,
                    stock.product.product_type,
                ]
            )
        return response

@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_brand(request):
    brand_csv = request.data.get('file', None)
    user = request.user
    
    file = NstyleFile.objects.create(
        file = brand_csv
    )
    brands_list = []
    try:
        with open( file.file.path , 'r', encoding='utf-8-sig', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                name = row.get('Product Name', None)
                website = row.get('Website', None)
                status_check = row.get('Status', None)
                description = row.get('Description', None)

                if all([website, status_check, description]) and (name not in ['', None]):
                    is_active = True if status_check == 'Active' else False
                    brands_list.append(
                        Brand(
                            name=name,
                            website=website,
                            description=description,
                            is_active=is_active
                        )
                    )
                else:
                    return Response(
                        {
                            'status' : False,
                            'status_code' : StatusCodes.MISSING_FIELDS_4001,
                            'status_code_text' : 'MISSING_FIELDS_4001',
                            'response' : {
                                'message' : 'Invalid Data!',
                                'error_message' : 'All fields are required.',
                            }
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            Brand.objects.bulk_create(brands_list)
            file.delete()
            return Response({'Status' : 'Success'})
    except:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'Error occured in uploading file',
                'response' : {
                    'message' : 'Something went wrong.',
                    'error_message' : 'Something went wrong.',
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_product(request):
    product_csv = request.data.get('file', None)
    user= request.user

    file = NstyleFile.objects.create(
        file = product_csv
    )           
    
    with open( file.file.path , 'r', encoding='utf-8') as imp_file:
        for index, row in enumerate(imp_file):
            if index == 0:
                continue
            row = row.split(',')
            row = row
            
            if len(row) < 10:
                continue
            name= row[0].strip('"')
            cost_price= row[1].strip('"')
            
            full_price= row[2].strip('"')
            sell_price= row[3].strip('"')
            quantity= row[4].strip('"')
            category= row[5].strip('"')
            brand = row[6].strip('"')
            product_type= row[7].strip('"')
            barcode_id= row[8].strip('"')
            vendor= row[9].replace('\n', '').strip('"')
            
            product= Product.objects.create(
                user=user,
                cost_price=cost_price,
                full_price=full_price,
                sell_price=sell_price,
                name = name,
                product_type=product_type,
                barcode_id=barcode_id
            )
            try:
                vendor_obj = BusinessVendor.objects.get(vendor_name=vendor)
                if vendor_obj is not None:
                    product.vendor = vendor_obj
                    product.save()
            except Exception as err:
                pass
            if len(brand) > 3:
                brand_obj = Brand.objects.filter(name=brand).order_by('is_active')
                if len(brand_obj) > 0:
                    brand_obj = brand_obj[0]
                    product.brand=brand_obj
                    product.save()
                else:
                    return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CATEGORY_BRAND_4020,
                    'response' : {
                    'message' : 'Brand not found',
                        }
                    }
                )
            else:
                return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CATEGORY_BRAND_4020,
                    'response' : {
                    'message' : 'Brand not found',
                        }
                    }
                )
                
            try:
                category_obj = Category.objects.get(name=category)
                if category_obj is not None:
                    product.category = category_obj
                    product.save()
                
            except Exception as err:
                return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CATEGORY_BRAND_4020,
                    'response' : {
                    'message' : 'Category not found',
                    'error_message' : str(err),
                        }
                    }
            )
            
            ProductStock.objects.create(
                user=user,
                product=product,
                quantity=quantity,
                
                
            )
            print(f'Added Product {name} ... {quantity} .... {product_type}...')

    file.delete()
    return Response({'Status' : 'Success'})
    
@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_category(request): 
    category_csv = request.data.get('file', None)


    file = NstyleFile.objects.create(
        file = category_csv
    )
    categories_list = []
    try:
        with open( file.file.path , 'r', encoding='utf-8-sig', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                name = row.get('Category Name', None)
                status_check = row.get('Status', None)

                if (status_check) and (name not in ['', None]):
                    status_flag = True if status_check == 'Active' else False
                    categories_list.append(
                        Category(name=name, is_active=status_flag)
                    )
                else:
                    return Response(
                        {
                            'status' : False,
                            'status_code' : StatusCodes.MISSING_FIELDS_4001,
                            'status_code_text' : 'MISSING_FIELDS_4001',
                            'response' : {
                                'message' : 'Invalid Data!',
                                'error_message' : 'Enter all the data',
                            }
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            Category.objects.bulk_create(categories_list)
            file.delete()
            return Response({'Status' : 'Success'})
    except:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'Error occured in uploading file',
                'response' : {
                    'message' : 'Something went wrong.',
                    'error_message' : 'Something went wrong.',
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    search_text = request.query_params.get('search_text', None)
    no_pagination = request.query_params.get('no_pagination', None)

    all_categories = Category.objects.order_by('-created_at')
    if search_text:
        all_categories = all_categories.filter(name__icontains=search_text)

    serialized = list(CategorySerializer(all_categories, many=True).data)

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'categories')

    return response

@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_category(request):
    name = request.data.get('name', None)
    is_active = request.data.get('is_active', False)
    if not all([name,]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'name',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    serialized = CategorySerializer(data=request.data)
    if serialized.is_valid():
        serialized.save()
        return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Category added!',
                    'error_message' : None,
                    'categories' : serialized.data
                }
            },
            status=status.HTTP_201_CREATED
        )
    else:
        return Response(
            {
                'status' : False,
                'status_code' : '400',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serialized.error_messages),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_category(request):
    category_id = request.data.get('category', None)
    if not all([category_id,]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'category',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        category = Category.objects.get(id=category_id)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CATEGORY_BRAND_4020,
                    'status_code_text' : 'INVALID_CATEGORY_BRAND_4020',
                    'response' : {
                        'message' : 'Category Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    serialized = CategorySerializer(category, data=request.data, partial=True)
    if serialized.is_valid():
        serialized.save()
        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Category updated!',
                    'error_message' : None,
                    'categories' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {
                'status' : False,
                'status_code' : '400',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serialized.error_messages),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_category(request):
    category_id = request.data.get('category', None)
    if not all([category_id,]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'category',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        category = Category.objects.get(id=category_id)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CATEGORY_BRAND_4020,
                    'status_code_text' : 'INVALID_CATEGORY_BRAND_4020',
                    'response' : {
                        'message' : 'Category Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    category.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Category deleted!',
                'error_message' : None,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_brands(request):
    search_text = request.query_params.get('search_text', None)
    no_pagination = request.query_params.get('no_pagination', None)

    all_brands = Brand.objects.order_by('-created_at')
    if search_text:
        all_brands = all_brands.filter(name__icontains=search_text)
        
    serialized = list(BrandSerializer(all_brands, many=True, context={'request' : request}).data)

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'brands')
    return response


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_brand(request):
    name = request.data.get('name', None)
    description = request.data.get('description', None)
    website = request.data.get('website', None)
    image = request.data.get('image', None)
    is_active = request.data.get('is_active', None)

    if not all([name]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'name',
                        'is_active',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    brand = Brand.objects.create(
        name=name,
        description=description,
        website=website,
        image=image,
    )
    if is_active is not None:
        brand.is_active = True
    else :
        brand.is_active = False
        
    brand.save()

    serialized = BrandSerializer(brand, context={'request' : request})
   
    return Response(
        {
            'status' : True,
            'status_code' : 201,
            'response' : {
                'message' : 'Brand Added!',
                'error_message' : None,
                'brand' : serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )

@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_brand(request):
    brand_id = request.data.get('brand', None)

    if brand_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'brand',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        brand = Brand.objects.get(id=brand_id)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CATEGORY_BRAND_4020,
                    'status_code_text' : 'INVALID_CATEGORY_BRAND_4020',
                    'response' : {
                        'message' : 'Brand Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
    
    brand.name = request.data.get('name', brand.name)
    brand.description = request.data.get('description', brand.description)
    brand.website = request.data.get('website', brand.website)
    brand.image = request.data.get('image', brand.image)
    is_active = request.data.get('is_active', None)
    if is_active is not None:
        brand.is_active = True
    else:
        brand.is_active = False
    brand.save()
    
    serialized = BrandSerializer(brand, context={'request' : request})
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Brand updated!',
                'error_message' : None,
                'brand' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
  

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_brand(request):
    brand_id = request.data.get('brand', None)

    if brand_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'brand',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        brand = Brand.objects.get(
            id=brand_id
        )
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CATEGORY_BRAND_4020,
                    'status_code_text' : 'INVALID_CATEGORY_BRAND_4020',
                    'response' : {
                        'message' : 'Category or Brand Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    brand.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Brand deleted!',
                'error_message' : None,
            }
        },
        status=status.HTTP_200_OK
    )

@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product(request):
    user = request.user
    business_id = request.data.get('business', None)
    vendor_id = request.data.get('vendor', None)
    category_id = request.data.get('category', None)
    product_size = request.data.get('size', None)
    brand_id = request.data.get('brand', None)
    product_type = request.data.get('product_type', 'Sellable')
    name = request.data.get('name', None)
    cost_price = request.data.get('cost_price', None)
    tax_rate = request.data.get('tax_rate', None)
    short_description = request.data.get('short_description', None)
    description = request.data.get('description', None)
    barcode_id = request.data.get('barcode_id', None)
    sku = request.data.get('sku', None)
    is_active = request.data.get('is_active', True)
    medias = request.data.getlist('product_images', None)
    
    #RetailPrice
    currency_retail_price = request.data.get('currency_retail_price', None)
    stock_status = request.data.get('stock_status', True)   
    alert_when_stock_becomes_lowest = request.data.get('alert_when_stock_becomes_lowest', None)
    invoices = request.data.get('invoices', None)

    
    product_error = []

    if not all([name,medias, brand_id, category_id, cost_price, sku,  stock_status ]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'business',
                        'category',
                        'brand',
                        'name',
                        'cost_price',
                        'full_price',
                        'sell_price',
                        'sku',
                        'product_images',
                        'status',
                        'quantity',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if is_active is not None:
        is_active = True #json.loads(stock_status)
    else: 
        is_active = False
        
    if stock_status is not None:
        stock_status = False #json.loads(stock_status)
    else: 
        stock_status = True
        
    if alert_when_stock_becomes_lowest  is not None:
        alert_when_stock_becomes_lowest= True #json.loads(alert_when_stock_becomes_lowest)
    else:
        alert_when_stock_becomes_lowest= False
    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    if vendor_id is not None:     
        try:
            vendor_id = BusinessVendor.objects.get(id=vendor_id, is_deleted=False, is_active=True)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.VENDOR_NOT_FOUND_4019,
                    'status_code_text' : 'VENDOR_NOT_FOUND_4019',
                    'response' : {
                        'message' : 'Vendor Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    try:
        category_id = Category.objects.get(id=category_id, is_active=True)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_CATEGORY_BRAND_4020,
                'status_code_text' : 'INVALID_CATEGORY_BRAND_4020',
                'response' : {
                    'message' : 'Category or Brand Not Found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
            
    try:
        brand_id = Brand.objects.get(id=brand_id, is_active=True)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_CATEGORY_BRAND_4020,
                'status_code_text' : 'INVALID_CATEGORY_BRAND_4020',
                'response' : {
                    'message' : 'Category or Brand Not Found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    location_ids = []
    product = Product.objects.create(
        user = user,
        business = business,
        vendor = vendor_id,
        category = category_id,
        brand = brand_id,
        product_type = product_type,
        name = name,
        cost_price = cost_price,
        product_size=product_size,
        tax_rate = tax_rate,
        short_description = short_description,
        description = description,
        barcode_id = barcode_id,
        sku = sku,
        slug = str(name).replace(' ' , '-').replace('/' , '-').replace('?' , '-'),
        is_active = is_active,
        published = True,
    )

    for img in medias:
        ProductMedia.objects.create(
            user=user,
            business=business,
            product=product,
            image=img,
            is_cover = True
        )
    if currency_retail_price is not None:
        if type(currency_retail_price) == str:
            currency_retail_price = currency_retail_price.replace("'" , '"')
            currency_retail_price = json.loads(currency_retail_price)

        elif type(currency_retail_price) == list:
            pass
        
        for retail in currency_retail_price:
            
            try:
                currency_id= Currency.objects.get(id=retail['currency'])
                
                CurrencyRetailPrice.objects.create(
                user = user,
                business = business,
                product = product,
                currency = currency_id,
                retail_price =  retail['retail_price'] ,
            )
            except Exception as err:
                print(str(err))
            
                    
    location_quantities = request.data.get('location_quantities', None)
    if location_quantities is not None:
        if type(location_quantities) == str:
            location_quantities = json.loads(location_quantities)
        
        for loc_quan in location_quantities:
            location_id = loc_quan.get('id', None)
            current_stock = loc_quan.get('current_stock', None)
            low_stock = loc_quan.get('low_stock', None)
            reorder_quantity = loc_quan.get('reorder_quantity', None)

            try:
                loc = BusinessAddress.objects.get(id = location_id)
                location_ids.append(str(loc))
            except Exception as err:
                ExceptionRecord.objects.create(text=str(err))
                pass
            
            else:
                product_stock = ProductStock.objects.create(
                    user = user,
                    business = business,
                    product = product,
                    location = loc,
                    available_quantity = current_stock,
                    low_stock = low_stock, 
                    reorder_quantity = reorder_quantity,
                    alert_when_stock_becomes_lowest = alert_when_stock_becomes_lowest,
                    is_active = stock_status,
                )

        try:
            location_remaing = BusinessAddress.objects.filter(is_deleted=False).exclude(id__in=location_ids)
            for i, location_id in enumerate(location_remaing):
                ProductStock.objects.create(
                        user = user,
                        business = business,
                        product = product,
                        location = location_id,
                        available_quantity = 0,
                        low_stock = 0, 
                        reorder_quantity = 0,
                        alert_when_stock_becomes_lowest = alert_when_stock_becomes_lowest,
                        is_active = stock_status,
                    )

        except Exception as err:
            product_error.append(str(err))

    else:
        ExceptionRecord.objects.create(text='No Location Quantities Find')
    
    if invoices is not None:
        if type(invoices) == str:
            invoices = invoices.replace("'" , '"')
            invoices = json.loads(invoices)
        else:
            pass
        for invoice in invoices:
            try:
                language = invoice['invoiceLanguage']
                product_name = invoice['product_name']
            except:
                pass
            else:
                productTranslation = ProductTranslations(
                    product = product,
                    product_name = product_name
                    )
                language = Language.objects.get(id__icontains = str(language))
                productTranslation.language = language
                productTranslation.save()

        # Hard coding the creation of english language translation
        # to keep the dynamic invoicingnlanguage in place.
        english_language = Language.objects.filter(name='English').first()
        ProductTranslations.objects.create(
            product=product,
            product_name=name,
            language=english_language
        )


    serialized = ProductSerializer(product, context={'request' : request, 'location': None})
    return Response(
        {
            'status' : True,
            'status_code' : 201,
            'response' : {
                'message' : 'Product added successfully',
                'error_message' : None,
                'errors': product_error,
                'product' : serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request):
    user = request.user
    product_id = request.data.get('product', None)
    vendor_id = request.data.get('vendor', None)
    category_id = request.data.get('category', None)
    brand_id = request.data.get('brand', None)
    location = request.data.get('location', None)
    is_active = request.data.get('is_active', None)
    
    currency_retail_price = request.data.get('currency_retail_price', None)
    invoices = request.data.get('invoices', None)

    check = True
    
    error = []

    if not all([product_id, category_id, brand_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'product',
                        'category',
                        'brand',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
            
    if vendor_id is not None:
        try:
            vendor = BusinessVendor.objects.get(id=vendor_id, is_deleted=False, is_active=True)
        except Exception as err:
            return Response(
                    {
                        'status' : False,
                        'status_code' : StatusCodes.VENDOR_NOT_FOUND_4019,
                        'status_code_text' : 'VENDOR_NOT_FOUND_4019',
                        'response' : {
                            'message' : 'Vendor Not Found',
                            'error_message' : str(err),
                        }
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
    else :
        vendor = None
    
    try:
        category = Category.objects.get(id=category_id, is_active=True)
        brand = Brand.objects.get(id=brand_id, is_active=True)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CATEGORY_BRAND_4020,
                    'status_code_text' : 'INVALID_CATEGORY_BRAND_4020',
                    'response' : {
                        'message' : 'Category or Brand Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    product = Product.objects.get(
        id=product_id,
        is_deleted = False,
        
    )
    if is_active is None:
        product.is_active = False
        product.save()
    images = request.data.getlist('product_images', None)

    if images is not None:
        for image in images:
            ProductMedia.objects.create(
                user = product.user, 
                business = product.business,
                product = product,
                image = image,
                is_cover = True
            )

    product.category = category
    product.brand = brand
    
    if vendor is not None:
        product.vendor = vendor
    product.save()
    
    data={}
    
    if type(location) == str:
            location = json.loads(location)
            
    product.location.clear()
    for loc in location:
        try:
            address=  BusinessAddress.objects.get(id = str(loc))
            product.location.add(address)
        except Exception as err:
            print(err)
    
    if currency_retail_price is not None:
        if check == True:
            vch = CurrencyRetailPrice.objects.filter(product = product_id)
            check = False
            for i in vch:
                try:
                    voucher = CurrencyRetailPrice.objects.get(id = i.id)
                    voucher.delete()
                except:
                    pass
        if type(currency_retail_price) == str:
            currency_retail_price = currency_retail_price.replace("'" , '"')
            currency_retail_price = json.loads(currency_retail_price)

        elif type(currency_retail_price) == list:
            pass
        
        for retail in currency_retail_price:
            currency_id = retail['currency']
            currency_id= Currency.objects.get(id=retail['currency'])
            
            CurrencyRetailPrice.objects.create(
            user = user,
            business = product.business,
            product = product,
            currency = currency_id,
            retail_price =  retail['retail_price'] ,
            )

    if invoices is not None:
        if type(invoices) == str:
            invoices = invoices.replace("'" , '"')
            invoices = json.loads(invoices)
        else:
            pass
        
        
        old_data = ProductTranslations.objects.filter(product=product)
        for old in old_data:
            old = ProductTranslations.objects.get(id = old.id)
            old.delete()

        for invoice in invoices:
            try:
                language = invoice['invoiceLanguage']
                product_name = invoice['product_name']
            except:
                pass
            else:
                productTranslation = ProductTranslations(
                    product = product,
                    product_name = product_name
                    )
                language = Language.objects.get(id__icontains = str(language))
                productTranslation.language = language
                productTranslation.save()

    
    # Hard coding the creation of english language translation
    # to keep the dynamic invoicing language in place.
    # old_product_name = request.data.get('name', None)
    # english_language = Language.objects.filter(name='English').first()
    # ProductTranslations.objects.create(
    #     product=product,
    #     product_name=old_product_name,
    #     language=english_language
    # )

    location_quantities = request.data.get('location_quantities', None)
    if location_quantities is not None:
        if type(location_quantities) == str:
            location_quantities = json.loads(location_quantities)
        
        for loc_quan in location_quantities:
            location_id = loc_quan.get('id', None)
            current_stock = loc_quan.get('current_stock', None)
            low_stock = loc_quan.get('low_stock', None)
            reorder_quantity = loc_quan.get('reorder_quantity', None)

            if all([location_id, ]):
                try:
                    loc = BusinessAddress.objects.get(id = location_id)
                except Exception as err:
                    ExceptionRecord.objects.create(text=str(err))
    
                    pass
                try:
                    product_stock = ProductStock.objects.get(product = product.id, location = loc.id )
                except Exception as err:
                    ExceptionRecord.objects.create(text=str(err))
                
                if reorder_quantity is not None:
                    product_stock.reorder_quantity = int(reorder_quantity) 
                    product_stock.save()
                product_stock.available_quantity = int(current_stock)
                product_stock.low_stock = int(low_stock)
                product_stock.save()

            else:
                ExceptionRecord.objects.create(text=f'fields not all {location_id}, {current_stock}, {low_stock}, {reorder_quantity}')

    else:
        ExceptionRecord.objects.create(text='No Location Quantities Find')
    
    
    serialized = ProductSerializer(product, data=request.data, partial=True, context={'request':request, 'location': None})
    if serialized.is_valid():
        serialized.save()
        data.update(serialized.data)
    
        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Product Updated!',
                    'error_message' : error,
                    'product' : data
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serialized.errors),
                    'product' : serialized.data
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
   
@api_view(['GET'])
@permission_classes([AllowAny])
def get_products(request):
    start_time = datetime.datetime.now()
    location_id = request.GET.get('location_id', None)
    search_text = request.query_params.get('search_text', None)
    quick_sales = request.query_params.get('quick_sales', False)
    
    query = Q(is_deleted=False)

    if quick_sales:
        query &= Q(is_active=True)

    if location_id:
        # Filter out those products which have product stock for this particular location
        product_ids = list(ProductStock.objects.filter(location__id=location_id).values_list('product__id', flat=True))
        query &= Q(id__in=product_ids)

    if search_text:
        #query building
        query &= Q(name__icontains=search_text)
        query |= Q(category__name__icontains=search_text)
        query |= Q(brand__name__icontains=search_text)
        query |= Q(product_type__icontains=search_text)

    all_products = Product.objects.prefetch_related(
        'location',
        'product_currencyretailprice',
        'products_stock_transfers',
        'consumptions',
        'product_medias',
        'product_stock',
    ).filter(query).order_by('-created_at')

    
    all_products_count = all_products.count()
    
    page_count = all_products_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    paginator = Paginator(all_products, 10)
    page_number = request.GET.get("page") 
    products = paginator.get_page(page_number)

    serialized = ProductSerializer(products, many=True, 
                                   context={'request' : request,
                                            'location': location_id,
                                            })
    data = serialized.data
    end_time = datetime.datetime.now()

    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'request' : {
                'seconds' : (end_time - start_time).seconds,
                'total_seconds' : (end_time - start_time).total_seconds(),
            },
            'response' : {
                'total_count' : len(all_products),
                'message' : 'All business Products!',
                'count':all_products_count,
                'pages':page_count,
                'per_page_result':10,
                'error_message' : None,
                'products' : data
            }
        },
        status=status.HTTP_200_OK
    )
   
@api_view(['GET'])
@permission_classes([AllowAny])
def get_products_optimized(request):
    # start_time = datetime.datetime.now()
    location_id = request.GET.get('location_id', None)
    search_text = request.query_params.get('search_text', None)
    quick_sales = request.query_params.get('quick_sales', False)
    
    query = Q(is_deleted=False)

    if quick_sales:
        query &= Q(is_active=True)

    if location_id:
        # Filter out those products which have product stock for this particular location
        product_ids = list(ProductStock.objects.filter(location__id=location_id).values_list('product__id', flat=True))
        query &= Q(id__in=product_ids)
    
    try:
        location = BusinessAddress.objects.get(id=location_id)
    except:
        location = None

    if search_text:
        #query building
        query &= Q(name__icontains=search_text)
        query |= Q(category__name__icontains=search_text)
        query |= Q(brand__name__icontains=search_text)
        query |= Q(product_type__icontains=search_text)

    all_products = Product.objects.prefetch_related(
        'location',
        'product_currencyretailprice',
        'products_stock_transfers',
        'consumptions',
        'product_medias',
        'product_stock',
    ).filter(query).order_by('-created_at')

    
    all_products_count = all_products.count()
    
    page_count = all_products_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    paginator = Paginator(all_products, 10)
    page_number = request.GET.get("page") 
    products = paginator.get_page(page_number)

    serialized = optSerializers.OtpimizedProductSerializer(products, many=True, 
                                   context={'request' : request,
                                            'location': location_id,
                                            'location_currency' : location.currency.id if location and location.currency else None
                                            })
    data = serialized.data
    # end_time = datetime.datetime.now()

    return Response(
        {
            'status' : True,
            'status_code' : 200,
            # 'request' : {
            #     'seconds' : (end_time - start_time).seconds,
            #     'total_seconds' : (end_time - start_time).total_seconds(),
            # },
            'response' : {
                'total_count' : len(all_products),
                'message' : 'All business Products!',
                'count':all_products_count,
                'pages':page_count,
                'per_page_result':10,
                'error_message' : None,
                'products' : data
            }
        },
        status=status.HTTP_200_OK
    )
   
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request):
    product_id = request.data.get('product', None)

    if not all([product_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'product',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        product = Product.objects.get(id=product_id, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Product not found or already deleted!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    product.is_deleted = True
    product.save()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Product deleted!',
                'error_message' : None,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def search_product(request):
    text = request.GET.get('text', None)

    if text is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'text',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    search_products = Product.objects.filter(
        Q(category__name__icontains=text) |
        Q(brand__name__icontains=text) |
        Q(product_type__icontains=text) |
        Q(name__icontains=text) |
        Q(short_description__icontains=text) |
        Q(description__icontains=text),
        is_active=True ,
        is_blocked=False ,
        is_deleted=False ,
    )
    serialized = ProductSerializer(search_products, many=True, context={'request':request})
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All Search Products!',
                'error_message' : None,
                'count' : len(serialized.data),
                'products' : serialized.data,
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_stocks(request):
    all_stocks = Product.objects.filter(is_active=True, is_deleted=False, product_stock__gt=0 ).order_by('-created_at').distinct()
    serialized = ProductWithStockSerializer(all_stocks, many=True, context={'request' : request}).data
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All stocks!',
                'error_message' : None,
                'stocks' : serialized
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_stock(request):
    stock_id = request.data.get('stock', None)

    if not all([stock_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'stock',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        stock = ProductStock.objects.get(id=stock_id, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Stock not found or already deleted!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    stock.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Stock deleted!',
                'error_message' : None,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def filter_stock(request):
    all_products = Product.objects.filter(
        is_active = True,
        is_deleted = False
    )[0:30]

    required_fields = ['vendor', 'brand', 'category', 'low_stock', 'high_stock', 'top_sellable_items', 'start_date', 'end_date']

    filter_funcs = {
        'vendor' : lambda product, value : True if str(product.vendor.id) == str(value) else False,
        'brand' : lambda product, value : True if str(product.brand.id) == str(value) else False,
        'category' : lambda product, value : True if str(product.category.id) == str(value) else False,
        'low_stock' : lambda product, value : True if int(product.product_stock.quantity) <= int(value) else False,
        'high_stock' : lambda product, value : True if int(product.product_stock.quantity) > int(value) else False,
        'top_sellable_items' : lambda product, value : True,
    }

    result = []
    for product in all_products:
        loop_return_value = False
        for field in required_fields:
            field_value = request.GET.get(field, None)
            if field_value is not None:
                try:
                    return_value = filter_funcs[field](product, field_value)
                    if not return_value:
                        continue
                    loop_return_value = True
                except Exception as err:
                    print(err)
                    loop_return_value = False

        if loop_return_value:
            result.append(product)
    
    serialized = ProductWithStockSerializer(result, many=True)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All filtered stocks Products!',
                'error_message' : None,
                'count' : len(result),
                'products' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def search_brand(request):
    text = request.GET.get('text', None)

    if text is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'text',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
    search_brand= Brand.objects.filter(
        Q(name__icontains=text)|
        Q(description=text)
    )
    serialized = BrandSerializer(search_brand, many=True, context={'request':request})
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All Search Products!',
                'error_message' : None,
                'count' : len(serialized.data),
                'Employees' : serialized.data,
            }
        },
        status=status.HTTP_200_OK
    )

@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_orderstock(request):
    user = request.user
    business = request.data.get('business', None)
    vendor = request.data.get('vendor', None)
    to_location = request.data.get('to_location',None)
    orstock_status = request.data.get('status',None)
    products = request.data.get('products', [])
    
    
    if not all([business, orstock_status, vendor, to_location]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                          'business',
                          'status',
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business_id=Business.objects.get(id=business)
    except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    try:
        vendor_id=BusinessVendor.objects.get(id=vendor)
    except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.VENDOR_NOT_FOUND_4019,
                    'response' : {
                    'message' : 'Vendor not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    try:
        to_location = BusinessAddress.objects.get(id=to_location)
    except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.LOCATION_NOT_FOUND_4017,
                    'response' : {
                    'message' : 'Location not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
    order = OrderStock.objects.create(
        user=user,
        business=business_id, 
        vendor = vendor_id,
        to_location= to_location,
        status =orstock_status,
    )
    if type(products) == str:
        products = products.replace("'" , '"')
        products = json.loads(products)
        pass
    else:
        pass
    for product in products :
        try:
            pro = Product.objects.get(id=product['id'])
        except Product.DoesNotExist:
            None
        OrderStockProduct.objects.create(
            order = order,
            product = pro,
            quantity = product['quantity']
        )
    serializer = OrderSerializer(order)
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Order Stock Created Successfully!',
                    'error_message' : None,
                    'orderstock' : serializer.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
 
@api_view(['GET'])
@permission_classes([AllowAny])
def get_orderstock(request):
    search_text = request.query_params.get('search_text', None)
    no_pagination = request.query_params.get('no_pagination', None)
    business_address_id = request.query_params.get('location_id', None)
    
    business_addr = BusinessAddress.objects.get(id=str(business_address_id))
    order_stocks = OrderStock.objects \
    .filter(
        is_deleted = False,                                      
        order_stock__product__is_deleted=False,
        to_location=business_addr) \
    .order_by('-created_at').distinct()
    
    if search_text:
        order_stocks = order_stocks.filter(id__icontains=search_text)
        
    serialized = list(OrderSerializer(order_stocks, many=True, context={'request' : request}).data)

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'stocks')
    return response

@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_orderstock(request):
    order_id = request.data.get('order_id', None)
    products = request.data.get('products', None)
    error = []
    if order_id is None:
            return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'User id is required',
                    'fields' : [
                        'order_id',
                    ]
                }
            },
             status=status.HTTP_400_BAD_REQUEST
           )
        
    try:
        order_stock = OrderStock.objects.get(id=order_id)
    except Exception as err:
              return Response(
             {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_ORDER_STOCK_ID_4038,
                    'status_code_text' : 'INVALID_ORDER_STOCK_ID_4038',
                        'response' : {
                            'message' : 'Order Stock Not Found',
                            'error_message' : str(err),
                    }
                },
                   status=status.HTTP_404_NOT_FOUND
              )
    if products is not None:
        if type(products) == str:
            products = products.replace("'" , '"')
            products = json.loads(products)

        for pro in products:
            id = pro.get('id', None)
            product_id = pro.get('product_id', None)
            is_deleted = pro.get('isDeleted', None)
            quantity = pro['quantity']     
            if id is not None:
                try:
                    pro_stock = OrderStockProduct.objects.get(id=id)
                    if is_deleted == 'True':
                        pro_stock.delete()
                        continue
                    
                    else:
                        pro_stock.quantity = quantity
                        pro_stock.save()
                except Exception as err:
                    error.append(str(err))     
            else:
                try:
                    pro = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    None
                OrderStockProduct.objects.create(
                    order = order_stock,
                    product = pro,
                    quantity = quantity
                )
 
    serializer = OrderSerializer(order_stock, data=request.data, partial=True, context={'request' : request})
    if serializer.is_valid():
           serializer.save()
    else: 
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
                'response' : {
                    'message' : 'Invialid Data',
                    'error_message' : str(serializer.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
        
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : ' OrderStock updated successfully',
                    'error_message' : None,
                    'stock' :serializer.data,
                    'Error':error,
                }
            },
            status=status.HTTP_200_OK
           )
        
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_orderstock(request):
    orderstock_id = request.data.get('id', None)

    if not all([orderstock_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        order = OrderStock.objects.get(id=orderstock_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Order Stock not found or already deleted!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    order.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Order Stock deleted!',
                'error_message' : None,
            }
        },
        status=status.HTTP_200_OK
    )

@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_orderstockproduct(request):
    user = request.user
    stockproduct_id = request.data.get('stockproduct_id', None)
    note = request.data.get('note', None)
    rec_quantity = request.data.get('rec_quantity', None)
    quantity = request.data.get('quantity', None)
    product_id = request.data.get('product_id', None)
    to_location = request.data.get('to_location', None)
    vendor_id = request.data.get('vendor_id', None)

    error = []
    if stockproduct_id is None:
            return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'User id is required',
                    'fields' : [
                        'order_id',
                    ]
                }
            },
             status=status.HTTP_400_BAD_REQUEST
           )
        
    try:
        order_stock = OrderStockProduct.objects.get(id=stockproduct_id)
    except Exception as err:
              return Response(
             {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_ORDER_STOCK_ID_4038,
                    'status_code_text' : 'INVALID_ORDER_STOCK_ID_4038',
                        'response' : {
                            'message' : 'Order Stock Product Not Found',
                            'error_message' : str(err),
                    }
                },
                   status=status.HTTP_404_NOT_FOUND
              )
    if note is not None:
        order_stock.note = note
        order_stock.save()
    if rec_quantity is not None:
        rec_quantity = order_stock.rec_quantity + int(rec_quantity)

        order_stock.rec_quantity = rec_quantity
        order_stock.save()
        exp = ExceptionRecord.objects.create(text= f'{order_stock.rec_quantity} ++ {rec_quantity}')
        exp.save()
    if int(rec_quantity) >= order_stock.quantity:
        order_stock.is_finished = True
    else:
        order_stock.is_finished = False
    
    try:
        product = Product.objects.get(id=product_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Product Not found',
                    'error_message' : str(err),
                    
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        location = BusinessAddress.objects.get(id=to_location)
    except:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Location Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        vendor=BusinessVendor.objects.get(id=vendor_id)
    except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.VENDOR_NOT_FOUND_4019,
                    'response' : {
                    'message' : 'Vendor not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    
    try:
        added_product = ProductStock.objects.get(product__id=product.id, location = location.id )
        stock_cunsumed = ProductOrderStockReport.objects.create(
            report_choice = 'Purchase',
            product = product,
            user = user,
            vendor = vendor,            
            location = location,
            quantity = int(rec_quantity), 
            reorder_quantity =int(quantity), 
            before_quantity = added_product.available_quantity  
            )
        # already_qunatity = int(added_product.order_quantity) - int(rec_quantity)
        
        # added_product.low_stock = already_qunatity
        # added_product.reorder_quantity = already_qunatity
        added_product.available_quantity += int(rec_quantity)
        added_product.save()
        stock_cunsumed.after_quantity = added_product.available_quantity
        stock_cunsumed.save()
        
    except Exception as err:
        ExceptionRecord.objects.create(
            is_resolved = True, 
            text= f'Issue raised in orderstockproduct quantity line 1795 {str(err)}'
        )
    
    serializer = OrderProductSerializer(order_stock, data=request.data, partial=True, context={'request' : request})
    if serializer.is_valid():
        created_obj = serializer.save()
        created_obj.rec_quantity = 0
        rec_quantity = order_stock.rec_quantity + int(rec_quantity)
        created_obj.rec_quantity = rec_quantity
        created_obj.save()
           
    else: 
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
                'response' : {
                    'message' : 'Invialid Data',
                    'error_message' : str(serializer.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
        
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Purchase order status is updated successfully',
                    'error_message' : None,
                    'stock' :serializer.data,
                    'Error':error,
                }
            },
            status=status.HTTP_200_OK
           )

@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_consumption(request):
    
    product_id = request.data.get('product', None)
    location_id = request.data.get('location', None)
    quantity = request.data.get('quantity', None)

    if not all([product_id, location_id, quantity]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'product',
                        'location',
                        'quantity',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        product = Product.objects.get(id=product_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Product Not found',
                    'error_message' : str(err),
                    
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        location = BusinessAddress.objects.get(id=location_id)
    except:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Location Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    cunsumption_obj = ProductConsumption.objects.create(
        user = request.user,
        product = product,
        location = location,
        quantity = quantity
    )
    try:
        consumed = ProductStock.objects.get(product__id=product.id, location = location.id )
        if consumed.available_quantity >= int(quantity):
            stock_cunsumed = ProductOrderStockReport.objects.create(
            report_choice = 'Consumed',
            product = product,
            user = request.user,
            consumed_location = location,
            quantity = int(quantity), 
            before_quantity = consumed.available_quantity     
            )
            sold = consumed.available_quantity - int(quantity)
            consumed.available_quantity = sold
            consumed.consumed_quantity +=  int(quantity)
            consumed.save()
            stock_cunsumed.after_quantity = sold
            stock_cunsumed.save()
        else:
            return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'available_quantity_less_then',
                'response' : {
                    'message' : 'Available_quantity less then quantity',
                    'error_message' : 'Quantity Error',
                    
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as err:
        ExceptionRecord.objects.create(
            is_resolved = True, 
            text= str(err)
        )
    

    serialized = ProductConsumptionSerializer(cunsumption_obj)

    

    return Response(
        {
            'status' : True,
            'status_code' : 201,
            'response' : {
                'message' : 'Product Consumption Created successfully',
                'error_message' : None,
                'product_consumption' : serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )

@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product_consumptions(request):
    
    consumption_id = request.data.get('consumption_id', None)
    user = request.user

    if not all([consumption_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'consumption_id',
                        'product',
                        'location',
                        'quantity',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        product_con = ProductConsumption.objects.get(id=consumption_id, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Product Comsumption Not found',
                    'error_message' : str(err),
                    
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    product_id = request.data.get('product', product_con.product.id)
    location_id = request.data.get('location', product_con.location.id)
    quantity = request.data.get('quantity', product_con.quantity)

    try:
        product = Product.objects.get(id=product_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Product Not found',
                    'error_message' : str(err),
                    
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        location = BusinessAddress.objects.get(id=location_id)
    except:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Location Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        
    )
    
    product_con.product = product
    product_con.location = location
    product_con.quantity = quantity
    product_con.save()
    
    try:
        consumed = ProductStock.objects.get(product__id=product, location = location )
        if consumed.available_quantity > int(quantity):
            sold = consumed.available_quantity - int(quantity)
            consumed.available_quantity = sold
            #consumed.sold_quantity += int(quantity)
            consumed.save()
            
        else:
            return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'available_quantity_less_then',
                'response' : {
                    'message' : 'Available_quantity less then quantity',
                    'error_message' : 'Quantity Error',
                    
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as err:
        ExceptionRecord.objects.create(
            is_resolved = True, 
            text= str(err)
        )
    
    serialized = ProductConsumptionSerializer(product_con)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Product Consumption Updated successfully',
                'error_message' : None,
                'product_consumption' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product_consumptions(request):
    consumption_id = request.data.get('consumption_id')
    if consumption_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'consumption_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        consumption = ProductConsumption.objects.get(id=consumption_id, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Product Consumption Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    else:
        consumption.is_deleted = True
        consumption.save()
        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Product Consumption Deleted successfully',
                    'error_message' : None,
                }
            },
            status=status.HTTP_200_OK
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_product_consumptions(request):
    search_text = request.query_params.get('search_text', None)
    no_pagination = request.query_params.get('no_pagination', None)
    location_id = request.query_params.get('location_id', None)
    
    product_consumptions = ProductConsumption.objects.filter(is_deleted=False).order_by('-created_at')

    if location_id:
        location = BusinessAddress.objects.get(id=str(location_id))
        product_consumptions = product_consumptions.filter(location=location)
    
    if search_text:
        query = Q(product__name__icontains=search_text)
        query |= Q(location__address_name__icontains=search_text)
        query |= Q(quantity_s__icontains=search_text)

        product_consumptions = product_consumptions.annotate(
            quantity_s=Cast('quantity', CharField())
        ).filter(query)
   
    serialized = list(ProductConsumptionSerializer(product_consumptions, many=True).data)

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'product_consumptions')
    return response


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_stock_transfer(request):
    
    product_id = request.data.get('product', None)
    from_location_id = request.data.get('from_location', None)
    to_location_id = request.data.get('to_location', None)
    quantity = request.data.get('quantity', None)
    note = request.data.get('note', None)

    if not all([product_id, from_location_id, to_location_id, quantity]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'product',
                        'from_location',
                        'to_location',
                        'quantity',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        product = Product.objects.get(id=product_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Product Not found',
                    'error_message' : str(err),
                    
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        from_location = BusinessAddress.objects.get(id=from_location_id)
        to_location = BusinessAddress.objects.get(id=to_location_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Location Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    cunsumption_obj = ProductStockTransfer.objects.create(
        user = request.user,
        product = product,
        from_location = from_location,
        to_location = to_location,
        quantity = quantity,
        note = note,
    )
    try:
        transfer = ProductStock.objects.get(product__id=product.id, location = from_location )
        if transfer.available_quantity >= int(quantity):
            stock_transfer = ProductOrderStockReport.objects.create(
            report_choice = 'Transfer_from',
            product = product,
            user = request.user,
            from_location = from_location,
            quantity = int(quantity), 
            before_quantity = transfer.available_quantity      
            )
            sold = transfer.available_quantity - int(quantity)
            transfer.available_quantity = sold
            transfer.save()
            stock_transfer.after_quantity = sold
            stock_transfer.save()
            
        try :
            transfer = ProductStock.objects.get(product__id=product.id, location = to_location )
            stock_transfer = ProductOrderStockReport.objects.create(
            report_choice = 'Transfer_to',
            product = product,
            user = request.user,
            to_location = to_location,
            quantity = int(quantity), 
            before_quantity = transfer.available_quantity      
            )
            sold = transfer.available_quantity + int(quantity)
            transfer.available_quantity = sold
            transfer.save()
            
            stock_transfer.after_quantity = sold
            stock_transfer.save()
            
        except Exception as err:
            ExceptionRecord.objects.create(
            is_resolved = True, 
            text= f'added id to location {str(err)}'
            )
        
    except Exception as err:
        ExceptionRecord.objects.create(
            is_resolved = True, 
            text= f'transfer id from location {str(err)}'
        )
    
    serialized = ProductStockTransferSerializer(cunsumption_obj)

    return Response(
        {
            'status' : True,
            'status_code' : 201,
            'response' : {
                'message' : 'Product Stock Transfer Created successfully',
                'error_message' : None,
                'product_stock_transfer' : serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_product_stock_transfers(request):
    search_text = request.query_params.get('search_text', None)
    no_pagination = request.query_params.get('no_pagination', None)

    stock_tranfers = ProductStockTransfer.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    if search_text:
        stock_tranfers = stock_tranfers.filter(product__name__icontains=search_text)

    serialized = list(ProductStockTransferSerializer(stock_tranfers, many=True).data)
    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'product_stock_transfers')
    return response 


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product_stock_transfer(request):
    stock_t_id = request.data.get('id', None)
    if not all([stock_t_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        stock_transfer = ProductStockTransfer.objects.get(id=stock_t_id, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Product Stock Transfer Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    else:
        stock_transfer.is_deleted = True
        stock_transfer.save()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Product Stock Transfer Deleted',
                'error_message' : None,
            }
        },
        status=status.HTTP_200_OK
    )

@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product_stock_transfer(request):
    stock_t_id = request.data.get('id', None)
    if not all([stock_t_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        stock_transfer = ProductStockTransfer.objects.get(id=stock_t_id, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Product Stock Transfer Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    else:
        product_id = request.data.get('product', stock_transfer.product.id)
        from_location_id = request.data.get('from_location',  stock_transfer.from_location.id)
        to_location_id = request.data.get('to_location',  stock_transfer.to_location.id)
        quantity = request.data.get('quantity',  stock_transfer.quantity)
        note = request.data.get('note',  stock_transfer.note)
        try:
            product = Product.objects.get(id=product_id)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : 404,
                    'status_code_text' : 'OBJECT_NOT_FOUND',
                    'response' : {
                        'message' : 'Product Not found',
                        'error_message' : str(err),
                        
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            from_location = BusinessAddress.objects.get(id=from_location_id)
            to_location = BusinessAddress.objects.get(id=to_location_id)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : 404,
                    'status_code_text' : 'OBJECT_NOT_FOUND',
                    'response' : {
                        'message' : 'Location Not found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        stock_transfer.product = product
        stock_transfer.from_location = from_location
        stock_transfer.to_location = to_location
        stock_transfer.quantity = quantity
        stock_transfer.note = note
        stock_transfer.save()

        serialized = ProductStockTransferSerializer(stock_transfer)

        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Product Stock Transfer Updated',
                    'error_message' : None,
                    'stock_transfer' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )
        
@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_stock_report(request):

    brand_id = request.GET.get('brand_id', None)
    query = request.GET.get('query', '')
    report_type = request.GET.get('report_type', None)
    location_id = request.GET.get('location_id', None)

    if not all([location_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'location_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        location = BusinessAddress.objects.get(
            id = location_id
        )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'LOCATION DOES NOT EXIST',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    


    filter_queries = {}

    if brand_id:
        filter_queries['brand__id'] = brand_id

    if report_type:
        filter_queries['product_stock_report__report_choice'] = report_type

    products = Product.objects.prefetch_related(
        'product_stock'
    ).filter(
        product_stock__location = location,
        is_deleted = False,
        name__icontains=query,
        **filter_queries
    ).distinct()
    
    serialized = list(ProductStockReportSerializer(
        products, 
        many = True,
        context = {
            'location_id' : location.id,
            'report_type' : report_type,
            'location_currency_id' : location.currency.id if location.currency else None,
        }
    ).data)
    
    paginator = CustomPagination()
    paginator.page_size = 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'product_stock_report')
    return response