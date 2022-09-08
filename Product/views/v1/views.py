

#from math import prod
from django.http import HttpResponse
from Utility.models import NstyleFile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
import json
import csv

from rest_framework.views import APIView
from rest_framework.settings import api_settings

# from django.shortcuts import render
# from rest_framework import generics
# import io, csv, pandas as pd
# from rest_framework.response import Response
# # remember to import the File model
# from Product.serializers import FileUploadSerializer , SaveFileSerializer
# from django.views.decorators.csrf import csrf_exempt


from NStyle.Constants import StatusCodes

from Product.models import Category, Brand , Product, ProductMedia, ProductStock
from Business.models import Business, BusinessAddress, BusinessVendor
from Product.serializers import CategorySerializer, BrandSerializer, ProductSerializer, ProductStockSerializer, ProductWithStockSerializer


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
def import_csv(request):
    product_csv = request.data.get('file', None)
    user= request.user
    #reader=csv.reader(product_csv)
    file = NstyleFile.objects.create(
        file = product_csv
    )
    print(file.file.path)
    with open( file.file.path , 'r', encoding='utf-8') as imp_file:
        for row in imp_file:
            row = row.split(',')
            row = row
            
            if len(row) < 10:
                continue
            name= row[0]
            cost_price= row[1]
            full_price= row[2]
            sell_price= row[3]
            quantity= row[4]
            category= row[5]
            brand= row[6]
            product_type= row[7] 
            barcode_id= row[8]
            vendor= row[9].replace('\n', '').strip()
            
            # name=row[0]
            # quantity= row[1]
            # category= row[2]
            # product_type = row[3].replace('\n', '').strip()
            
            product= Product.objects.create(
                user=user,
                cost_price=cost_price,
                full_price=full_price,
                name = name,
                product_type=product_type,
                barcode_id=barcode_id
            )
            # product.category=category
            # product.save()
                # name=name, 
                # cost_price=cost_price,
                # full_price=full_price,
                # product_type=product_type, 
                # brand=brand,
                # barcode_id=barcode_id,
                # vendor=vendor
            
            
            try:
                print(vendor)
                vendor_obj = BusinessVendor.objects.get(vendor_name=vendor)
                if vendor_obj is not None:
                    product.vendor = vendor_obj
                    product.save()
            # else:
            #         pass
            except Exception as err:
                return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Vendor not found',
                    'error_message' : str(err),
                    }
                    }
                )
            
            try:
                brand_obj = Brand.objects.get(name=brand)
                if brand_obj is not None:
                    product.brand = brand_obj
                    product.save()
                
            except Exception as err:
                return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Brand not found',
                    'error_message' : str(err),
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
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
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

    if not all([name, image]):
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
                        'image',
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

    # Product Stock Details 
    quantity = request.data.get('quantity', None)
    unit = request.data.get('unit', None)
    amount = request.data.get('amount', None)
    stock_status = request.data.get('stock_status', None)
   
    alert_when_stock_becomes_lowest = request.data.get('alert_when_stock_becomes_lowest', None)
   

    if not all([name,medias, brand_id, category_id, cost_price, full_price, sell_price, sku, quantity, stock_status ]):
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
    if stock_status is not None:
        stock_status = json.loads(stock_status)
    else: 
        stock_status = True
    if alert_when_stock_becomes_lowest  is not None:
        alert_when_stock_becomes_lowest= json.loads(alert_when_stock_becomes_lowest)
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
    
    product = Product.objects.create(
        user = user,
        business = business,
        vendor = vendor_id,
        category = category_id,
        brand = brand_id,
        product_type = product_type,
        name = name,
        cost_price = cost_price,
        full_price = full_price,
        sell_price = sell_price,
        tax_rate = tax_rate,
        short_description = short_description,
        description = description,
        barcode_id = barcode_id,
        sku = sku,
        slug = str(name).replace(' ' , '-').replace('/' , '-').replace('?' , '-'),
        is_active=True,
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
    
    ProductStock.objects.create(
        user = user,
        business = business,
        product = product ,
        quantity = quantity,
        amount = amount,
        unit = unit,
        available_quantity= quantity,
        alert_when_stock_becomes_lowest = alert_when_stock_becomes_lowest,
        is_active = stock_status,
    )

    serialized = ProductSerializer(product, context={'request' : request})
    return Response(
        {
            'status' : True,
            'status_code' : 201,
            'response' : {
                'message' : 'Product Added!',
                'error_message' : None,
                'product' : serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request):
    product_id = request.data.get('product', None)
    vendor_id = request.data.get('vendor', None)
    category_id = request.data.get('category', None)
    brand_id = request.data.get('brand', None)

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
    )
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
    
    stock=ProductStock.objects.get(product=product)
    serialized= ProductStockSerializer(stock, data=request.data, partial=True)
    if serialized.is_valid():
        serialized.save()
        data.update(serialized.data)
        
    
    serialized = ProductSerializer(product, data=request.data, partial=True, context={'request':request})
    if serialized.is_valid():
        serialized.save()
        data.update(serialized.data)
    
        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Product Updated!',
                    'error_message' : None,
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
    all_products = Product.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = ProductSerializer(all_products, many=True, context={'request' : request})

    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All business Products!',
                'error_message' : None,
                'products' : serialized.data
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
    all_stocks = Product.objects.filter(is_active=True, is_deleted=False, product_stock__gt=0 )
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
