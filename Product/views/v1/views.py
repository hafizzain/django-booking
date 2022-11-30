from cmath import cos
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


from NStyle.Constants import StatusCodes

from Product.models import ( Category, Brand , Product, ProductMedia, ProductStock
                            , OrderStock, OrderStockProduct, ProductConsumption
                           )
from Business.models import Business, BusinessAddress, BusinessVendor
from Product.serializers import (CategorySerializer, BrandSerializer, ProductSerializer, ProductStockSerializer, ProductWithStockSerializer
                                 ,OrderSerializer , OrderProductSerializer, ProductConsumptionSerializer
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
            
            if len(row) < 3:
                continue
            name =  row[0].strip('"')
            website =  row[1].strip('"')
            description =  row[2].strip('"')
            brand = Brand.objects.create(
                #user = user,
                name=name,
                description=description,
                website=website,
            )
            
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
            
            if len(row) < 2:
                continue
            name = row[0].strip('"')
            active=row[1].replace('\n', '').strip('"')
            
            if active == 'Active':
                active = True
            else:
                active = False
                
                
            Category.objects.create(
                name = name,
                is_active=active,
            )  
            
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
    product_size = request.data.get('product_size', None)
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
    
    # location = request.data.get('location', None)

    # Product Stock Details 
    # quantity = request.data.get('quantity', None)
    # sellable_quantity = request.data.get('sellable_quantity', None)
    # consumable_quantity = request.data.get('consumable_quantity',None)
    # unit = request.data.get('unit', None)
    # product_unit = request.data.get('product_unit', None)
    # amount = request.data.get('amount', None)
    stock_status = request.data.get('stock_status', None)

    #turnover = request.data.get('turnover', None)
   
    alert_when_stock_becomes_lowest = request.data.get('alert_when_stock_becomes_lowest', None)
    
    product_error = []

    if not all([name,medias, brand_id, category_id, cost_price, full_price, sell_price, sku,  stock_status ]):
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
        product_size=product_size,
        tax_rate = tax_rate,
        short_description = short_description,
        description = description,
        barcode_id = barcode_id,
        sku = sku,
        slug = str(name).replace(' ' , '-').replace('/' , '-').replace('?' , '-'),
        is_active=True,
        published = True,
    )
    # if type(location) == str:
    #         location = json.loads(location)

    # elif type(location) == list:
    #         pass
        
    # for loc in location:
    #     try:
    #         location_id = BusinessAddress.objects.get(id=loc)  
    #         print(location_id)
    #         product.location.add(location_id)
    #     except Exception as err:
    #         product_error.append(str(err))


    for img in medias:
        ProductMedia.objects.create(
            user=user,
            business=business,
            product=product,
            image=img,
            is_cover = True
        )
    
    location_quantities = request.data.get('location_quantities', None)
    if location_quantities is not None:
        if type(location_quantities) == str:
            location_quantities = json.loads(location_quantities)
        
        for loc_quan in location_quantities:
            location_id = loc_quan.get('id', None)
            current_stock = loc_quan.get('current_stock', None)
            low_stock = loc_quan.get('low_stock', None)
            reoreder_quantity = loc_quan.get('reoreder_quantity', None)

            if all([location_id, current_stock, low_stock, reoreder_quantity]):
                try:
                    loc = BusinessAddress.objects.get(id = location_id)
                except:
                    pass
                else:
                    product_stock = ProductStock.objects.create(
                        user = user,
                        business = business,
                        product = product,
                        location = loc,
                        available_quantity = current_stock,
                        low_stock = low_stock, 
                        reorder_quantity = reoreder_quantity,
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
                'errors': product_error,
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
    location = request.data.get('location', None)

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
    
    if type(location) == str:
            location = json.loads(location)
            
    product.location.clear()
    for loc in location:
        try:
            address=  BusinessAddress.objects.get(id = str(loc))
            product.location.add(address)
        except Exception as err:
            print(err)
            
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
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_orderstock(request):
    user = request.user
    business = request.data.get('business', None)
    
    vendor = request.data.get('vendor', None)
    location = request.data.get('location',None)
    orstock_status = request.data.get('status',None)
    rec_quantity = request.data.get('rec_quantity',None)
    
    products = request.data.get('products', [])
    #quantity = request.data.get('quantity',None)
    
    
    if not all([business, orstock_status, vendor, location]):
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
        location_id=BusinessAddress.objects.get(id=location)
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
        location= location_id,
        status =orstock_status,
        rec_quantity= rec_quantity
    )
    print(type(products))
    if type(products) == str:
        products = products.replace("'" , '"')
        print(products)
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
    order_stocks = OrderStock.objects.filter(is_deleted = False, order_stock__product__is_deleted=False).order_by('-created_at')
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
    #products = request.data.get('products', [])
    
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
                    'stock' :serializer.data
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
                        'product',
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_cunsumption(request):
    
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_product_cunsumptions(request):
    
    product_consumptions = ProductConsumption.objects.all()
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