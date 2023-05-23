from cmath import cos
from threading import Thread
from django.http import HttpResponse
from Product.Constants.Add_Product import add_product_remaing
from Utility.models import Currency, NstyleFile, ExceptionRecord
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
import json
import csv
import datetime
from rest_framework.views import APIView
from rest_framework.settings import api_settings


from NStyle.Constants import StatusCodes

from Product.models import ( Category, Brand, CurrencyRetailPrice , Product, ProductMedia, ProductOrderStockReport, ProductStock
                            , OrderStock, OrderStockProduct, ProductConsumption, ProductStockTransfer
                           )
from Business.models import Business, BusinessAddress, BusinessVendor
from Product.serializers import (CategorySerializer, BrandSerializer, ProductOrderStockReportSerializer, ProductSerializer, ProductStockSerializer, ProductWithStockSerializer
                                 ,OrderSerializer , OrderProductSerializer, ProductConsumptionSerializer, ProductStockTransferSerializer, ProductOrderSerializer, ProductStockReportSerializer
                                 )
from django.core.paginator import Paginator


@api_view(['GET'])
@permission_classes([AllowAny])
def get_test_api(request):
    product_id = request.data.get('product_id', None)
    from_location_id = request.data.get('from_location_id', None)
    # service_id = "ed9b3e32-4f1f-469a-a065-ea9805ee0edc"
    # location = "fef70b9b-c42d-4b3e-bf54-f4d1b5513f6b"
    # product = Product.objects.get(id = service_id)
    # product_stock = product.product_stock.all()#.first()
    # available = 0
    # for i in product_stock:
    #     print(location, i.location)
    #     if location == str(i.location):
    #         print(i.available_quantity)
    # #data = product_stock.available_quantity
    # data = 1
    # print(data)
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
    
        #data =  ProductStockTransfer.objects.filter(product = i).aggregate(Sum('quantity'))
    #print(data)
    
    # product = Product.objects.filter(is_deleted = False).exclude(id__in = data)
    # for i in product:
    #     print('test')
    
    # try:
    #     added = ProductStock.objects.get(product__id=product_id, location = str(from_location_id) )
    #     print(added)
    #     # sold = added.available_quantity - 3
    #     # added.available_quantity = sold
    #     # added.save()
    #     # print(sold)
    #     # print(added.available_quantity)
    # except Exception as err:
    #     print(err)
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
        #product = ProductStock.objects.all()
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_brand(request):
    brand_csv = request.data.get('file', None)
    user= request.user
    
    file = NstyleFile.objects.create(
        file = brand_csv
    )
    with open( file.file.path , 'r', encoding='utf-8') as imp_file:
        for index, row in enumerate(imp_file):
            if index == 0:
                continue
            row = row.split(',')
            row = row
            
            if len(row) < 5:
                continue
            name =  row[0].strip('"')
            website =  row[1].strip('"')
            status =  row[2].strip('"')
            description =  row[3].strip('"')
            #image =  row[4].strip('"')
            brand = Brand.objects.create(
                #user = user,
                name=name,
                description=description,
                website=website,
                #image=image,
            )
            if status == 'Active':
                brand.is_active = True
                brand.save()
            else:
                brand.is_active = False
                brand.save()
            
    file.delete()
    return Response({'Status' : 'Success'})
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_product(request):
    product_csv = request.data.get('file', None)
    user= request.user

    file = NstyleFile.objects.create(
        file = product_csv
    )           
    
    #print(file.file.path)
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
                # Q(name__icontains=brand) | Q(is_active__icontains= True) | Q(website__isnull=True)
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
            
            
            # Category.objects.create(
            #     product=product, 
                
            # )
            
            ProductStock.objects.create(
                user=user,
                product=product,
                quantity=quantity,
                
                
            )
            print(f'Added Product {name} ... {quantity} .... {product_type}...')

    file.delete()
    return Response({'Status' : 'Success'})
    
 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_category(request): 
    user = request.user
    category_csv = request.data.get('file', None)


    file = NstyleFile.objects.create(
        file = category_csv
    )
    with open( file.file.path , 'r', encoding='utf-8') as imp_file:
        for index, row in enumerate(imp_file):
            if index == 0:
                continue
            row = row.split(',')
            row = row
            
            if len(row) < 3:
                continue
            name = row[0].strip('"')
            active=row[2].replace('\n', '').strip('"')
            
            category = Category.objects.create(
                name = name,
                #is_active=active,
            )  
            if active == 'Active':
               category.active = True
               category.save()
            else:
                category.active  = False
                category.save()
                
    file.delete()
    return Response({'Status' : 'Success'})

@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    all_categories = Category.objects.all().order_by('-created_at')
    serialized = CategorySerializer(all_categories, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Categories',
                'error_message' : None,
                'categories' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

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
                    'message' : 'Category Added!',
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
    all_brands = Brand.objects.all()
    serialized = BrandSerializer(all_brands, many=True, context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Brands',
                'error_message' : None,
                'brands' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


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
                        # 'image',
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
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product(request):
    user = request.user
    business_id = request.data.get('business', None)
    vendor_id = request.data.get('vendor', None)
    category_id = request.data.get('category', None)
    product_size = request.data.get('size', None)
    #image = request.data.getlist('image', None)
    brand_id = request.data.get('brand', None)
    product_type = request.data.get('product_type', 'Sellable')
    name = request.data.get('name', None)
    cost_price = request.data.get('cost_price', None)
    full_price = request.data.get('full_price', None)
    sell_price = request.data.get('sell_price', None)
    tax_rate = request.data.get('tax_rate', None)
    short_description = request.data.get('short_description', None)
    description = request.data.get('description', None)
    barcode_id = request.data.get('barcode_id', None)
    sku = request.data.get('sku', None)
    is_active = request.data.get('is_active', True)
    medias = request.data.getlist('product_images', None)
    
    #RetailPrice
    currency_retail_price = request.data.get('currency_retail_price', None)
    
    # location = request.data.get('location', None)

    # Product Stock Details 
    # quantity = request.data.get('quantity', None)
    # sellable_quantity = request.data.get('sellable_quantity', None)
    # consumable_quantity = request.data.get('consumable_quantity',None)
    # unit = request.data.get('unit', None)
    # product_unit = request.data.get('product_unit', None)
    # amount = request.data.get('amount', None)
    stock_status = request.data.get('stock_status', True)

    #turnover = request.data.get('turnover', None)
   
    alert_when_stock_becomes_lowest = request.data.get('alert_when_stock_becomes_lowest', None)
    
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
        #full_price = full_price,
        #sell_price = sell_price,
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
            #currency_id = retail['currency']
            #price = retail['retail_price']
            
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
                #ExceptionRecord.objects.create(is_resolved = False, text=f'currency not found product line 866  ' )
            
                    
    location_quantities = request.data.get('location_quantities', None)
    if location_quantities is not None:
        if type(location_quantities) == str:
            #ExceptionRecord.objects.create(is_resolved = True, text='Location Quantities was string and gonna convert')
            location_quantities = json.loads(location_quantities)
            #ExceptionRecord.objects.create(is_resolved = True, text='Converted')
        
        for loc_quan in location_quantities:
            location_id = loc_quan.get('id', None)
            current_stock = loc_quan.get('current_stock', None)
            low_stock = loc_quan.get('low_stock', None)
            reorder_quantity = loc_quan.get('reorder_quantity', None)

            #if all([location_id, current_stock, low_stock, reorder_quantity]):
            try:
                loc = BusinessAddress.objects.get(id = location_id)
                #ExceptionRecord.objects.create(text=loc)
                location_ids.append(str(loc))
            except Exception as err:
                ExceptionRecord.objects.create(text=str(err))
                pass
            
            else:
                #ExceptionRecord.objects.create(text=f'{current_stock} {low_stock}  reorder_quantity{reorder_quantity}')
                product_stock = ProductStock.objects.create(
                    user = user,
                    business = business,
                    product = product,
                    location = loc,
                    available_quantity = current_stock,
                    #order_quantity = current_stock,
                    low_stock = low_stock, 
                    reorder_quantity = reorder_quantity,
                    alert_when_stock_becomes_lowest = alert_when_stock_becomes_lowest,
                    is_active = stock_status,
                )

            # else:
            #     ExceptionRecord.objects.create(text=f'fields not all {location_id}, {current_stock}, {low_stock}, {reorder_quantity}')
                
        try:
            location_remaing = BusinessAddress.objects.filter(is_deleted = False).exclude(id__in = location_ids)
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
        #         try:
        #             thrd = Thread(target=add_product_remaing, args=[], kwargs={'product' : product, 'business' : business, 'location': location_id})
        #             thrd.start()
        #         except Exception as err:
        #             ExceptionRecord.objects.create(
        #                 text=str(err)
        # )
        except Exception as err:
            product_error.append(str(err))

    else:
        ExceptionRecord.objects.create(text='No Location Quantities Find')
    

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
                        # 'vendor',
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
            
    # all_stocks = ProductStock.objects.filter(product=product)
    # for stk in all_stocks:
    #     stk.delete()
    
    if currency_retail_price is not None:
        if type(currency_retail_price) == str:
            currency_retail_price = currency_retail_price.replace("'" , '"')
            currency_retail_price = json.loads(currency_retail_price)

        elif type(currency_retail_price) == list:
            pass
        
        for retail in currency_retail_price:
            currency_id = retail['currency']
            id = retail.get('id', None)
            price = retail['retail_price']
            
            if id is not None:
                try:
                    currency_retail = CurrencyRetailPrice.objects.get(id=retail['id'])
                    is_deleted = retail.get('is_deleted', None)
                    if bool(is_deleted) == True:
                        currency_retail.delete()
                        continue
                    currency_id= Currency.objects.get(id=retail['currency'])
                    currency_retail.currency = currency_id
                    currency_retail.retail_price = retail['retail_price']
                    currency_retail.save()
                except Exception as err:
                    error.append(str(err))
                    print(err)
            else:
                currency_id= Currency.objects.get(id=retail['currency'])
                
                CurrencyRetailPrice.objects.create(
                user = user,
                business = product.business,
                product = product,
                currency = currency_id,
                retail_price =  retail['retail_price'] ,
                )
            
                

    location_quantities = request.data.get('location_quantities', None)
    if location_quantities is not None:
        if type(location_quantities) == str:
            #ExceptionRecord.objects.create(is_resolved = True, text='Location Quantities was string and gonna convert')
            location_quantities = json.loads(location_quantities)
            #ExceptionRecord.objects.create(is_resolved = True, text='Converted')
        
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
                
                
                # else:
                #     product_stock = ProductStock.objects.create(
                #         user = request.user,
                #         business = product.business,
                #         product = product,
                #         location = loc,
                #         available_quantity = current_stock,
                #         low_stock = low_stock, 
                #         reorder_quantity = reorder_quantity,
                #         alert_when_stock_becomes_lowest = True,
                #         is_active = True
                #     )
                #     ExceptionRecord.objects.create(is_resolved = True, text ='Created')

            else:
                ExceptionRecord.objects.create(text=f'fields not all {location_id}, {current_stock}, {low_stock}, {reorder_quantity}')

    else:
        ExceptionRecord.objects.create(text='No Location Quantities Find')
    
    # serialized= ProductStockSerializer(stock, data=request.data, partial=True)
    # if serialized.is_valid():
    #     serialized.save()
    #     data.update(serialized.data)
        
    
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
    location = request.GET.get('location_id', None)
    
    all_products = Product.objects.prefetch_related(
        'location',
        'product_currencyretailprice',
        'products_stock_transfers',
        'consumptions',
        'product_medias',
        'product_stock',
    ).filter(is_deleted=False, is_active=True).order_by('-created_at')
    
    all_products_count = all_products.count()
    
    page_count = all_products_count / 20
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    paginator = Paginator(all_products, 20)
    page_number = request.GET.get("page") 
    products = paginator.get_page(page_number)

    serialized = ProductSerializer(products, many=True, 
                                   context={'request' : request,
                                            'location': location,
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
                'page_count':page_count,
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
        #product_stock = ProductStock.objects.get(product = product , is_deleted=False )
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

    #product.is_deleted = True
    #product_stock.is_deleted = True
    #product.save()
    product.delete()
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
    serialized = ProductWithStockSerializer(all_stocks, many=True, context={'request' : request})
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All stocks!',
                'error_message' : None,
                'stocks' : serialized.data
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
        # 'start_date' : lambda product, value : True if product.created_at > value else False,
        # 'end_date' : lambda product, value : True if product.created_at < value else False,
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
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_orderstock(request):
    user = request.user
    business = request.data.get('business', None)
    
    vendor = request.data.get('vendor', None)
    #from_location = request.data.get('from_location',None)
    to_location = request.data.get('to_location',None)
    orstock_status = request.data.get('status',None)
    rec_quantity = request.data.get('rec_quantity',None)
    
    products = request.data.get('products', [])
    #quantity = request.data.get('quantity',None)
    
    
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
        #from_location = BusinessAddress.objects.get(id=from_location)
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
        #from_location= from_location,
        to_location= to_location,
        status =orstock_status,
        #rec_quantity= rec_quantity
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
    order_stocks = OrderStock.objects.filter(is_deleted = False, order_stock__product__is_deleted=False).order_by('-created_at').distinct()
    serialized = OrderSerializer(order_stocks, many=True, context={'request' : request})
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All Order stocks!',
                'error_message' : None,
                'stocks' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
 
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
    
    # if type(products) == str:
    #     products = products.replace("'" , '"')
    #     print(products)
    #     products = json.loads(products)
    # else:
    #     pass
    # for product in products :
       
    #     if product['edit'] == 'yes':
    #         try:
    #             print(product['id'])
    #             id_dt = OrderStockProduct.objects.get(id=product['id'])
    #             pro = Product.objects.get(id=product['product_id'])
    #         except Product.DoesNotExist:
    #             None
            
    #         product_serializer = OrderProductSerializer(id_dt, data=request.data , partial=True)
       
              
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
        order_stock.rec_quantity = rec_quantity
        order_stock.save()
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
                    'message' : 'Purchase order status is updated successfully',
                    'error_message' : None,
                    'stock' :serializer.data,
                    'Error':error,
                }
            },
            status=status.HTTP_200_OK
           )

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
            #location = product_location,
            consumed_location = location,
            quantity = int(quantity), 
            before_quantity = consumed.available_quantity     
            )
            sold = consumed.available_quantity - int(quantity)
            consumed.available_quantity = sold
            consumed.consumed_quantity +=  int(quantity)
            #consumed.sold_quantity += int(quantity)
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
    
    product_consumptions = ProductConsumption.objects.filter(is_deleted=False)
    serialized = ProductConsumptionSerializer(product_consumptions, many=True)

    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Product Consumption Created successfully',
                'error_message' : None,
                'product_consumptions' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

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
        #product_location = BusinessAddress.objects.get(id=product.location.id)
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
            #location = product_location,
            from_location = from_location,
            quantity = int(quantity), 
            before_quantity = transfer.available_quantity      
            )
            sold = transfer.available_quantity - int(quantity)
            transfer.available_quantity = sold
            #transfer.sold_quantity += int(quantity)
            transfer.save()
            stock_transfer.after_quantity = sold
            stock_transfer.save()
            
        try :
            transfer = ProductStock.objects.get(product__id=product.id, location = to_location )
            stock_transfer = ProductOrderStockReport.objects.create(
            report_choice = 'Transfer_to',
            product = product,
            user = request.user,
            #location = product_location,
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
    stock_tranfers = ProductStockTransfer.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    serialized = ProductStockTransferSerializer(stock_tranfers, many=True)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Product Stock Transfers',
                'error_message' : None,
                'product_stock_transfers' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

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
    # stock_report = ProductOrderStockReport.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    
    # grouped_reports = {}
    # for report in stock_report:
    #     product_id = report.product.id
    #     if product_id not in grouped_reports:
    #         grouped_reports[product_id] = []
    #     grouped_reports[product_id].append(report)
    
    # serialized_data = []
    
    # # Serialize the grouped data
    # for product_id, reports in grouped_reports.items():
    #     product = reports[0].product
    #     serialized_reports = ProductOrderStockReportSerializer(reports, many=True).data
    #     serialized_data.append({
    #         'product': ProductOrderSerializer(product).data,
    #         'reports': serialized_reports
    #     })

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


    products = Product.objects.prefetch_related(
        'product_stock'
    ).filter(
        product_stock__location = location,
        is_deleted = False
    )
    
    serialized = ProductStockReportSerializer(
        products, 
        many = True,
        context = {
            'location_id' : location.id,
            'location_currency_id' : location.currency.id if location.currency else None
        }
    )
    data = serialized.data

    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Product Stock Reports',
                'error_message' : None,
                'product_stock_report' : data
            }
        },
        status=status.HTTP_200_OK
    )