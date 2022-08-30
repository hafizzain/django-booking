


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
import json

from NStyle.Constants import StatusCodes


from Product.models import Category, Brand, Product, ProductMedia, ProductStock
from Business.models import Business, BusinessAddress, BusinessVendor
from Product.serializers import CategorySerializer, BrandSerializer, ProductSerializer, ProductStockSerializer, ProductWithStockSerializer



def ExportCSV(request):
        #product = ProductStock.objects.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ProductStock.csv"'

        writer = csv.writer(response)
        writer.writerow('id', 'user', 'business', 'product', 'quantity', 'amount', 'unit', 'is_active')
        
        for product in ProductStock.objects.all():
            writer.writerow(product)
        return response



@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    all_categories = Category.objects.all()
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
    is_active = request.data.get('is_active', False)

    if not all([name, description, website, image]):
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
                        'description',
                        'website',
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
        is_active=is_active
    )
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
        is_active = json.loads(is_active)
    else:
        is_active = True
        
    brand.is_active
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
    product_type = request.data.get('product_type', None)
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
   

    if not all([name, business_id, vendor_id, category_id, brand_id, product_type, cost_price, full_price, sell_price, short_description, description, barcode_id, sku, quantity, unit, amount,alert_when_stock_becomes_lowest ]):
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
                        'vendor',
                        'category',
                        'brand',
                        'product_type',
                        'name',
                        'cost_price',
                        'full_price',
                        'sell_price',
                        'tax_rate',
                        'short_description',
                        'description',
                        'barcode_id',
                        'sku',
                        'product_images',
                        'quantity', 
                        'unit', 
                        'amount', 
                        'alert_when_stock_becomes_lowest'
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
        alert_when_stock_becomes_lowest= True
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
    
    product = Product.objects.create(
        user = user,
        business = business,
        vendor = vendor,
        category = category,
        brand = brand,
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
            image=img
        )
    
    ProductStock.objects.create(
        user = user,
        business = business,
        product = product ,
        quantity = quantity,
        amount = amount,
        unit = unit,
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

    if not all([product_id, vendor_id, category_id, brand_id]):
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
                        'vendor',
                        'category',
                        'brand',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
            
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
    product.category = category
    product.brand = brand
    product.vendor = vendor
    product.save()

    serialized = ProductSerializer(product, data=request.data, partial=True, context={'request':request})
    if serialized.is_valid():
        serialized.save()
        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Product Updated!',
                    'error_message' : None,
                    'product' : serialized.data
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
    all_products = Product.objects.filter(is_deleted=False)
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
    serialized = ProductWithStockSerializer(all_stocks, many=True)
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
