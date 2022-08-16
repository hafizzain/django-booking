


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from NStyle.Constants import StatusCodes

from Product.models import Category, Brand, Product, ProductMedia, ProductStock
from Business.models import Business, BusinessAddress
from Product.serializers import CategorySerializer, BrandSerializer, ProductSerializer

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



@api_view(['GET'])
@permission_classes([AllowAny])
def get_brands(request):
    all_brands = Brand.objects.all()
    serialized = BrandSerializer(all_brands, many=True)
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product(request):
    user = request.user
    business_id = request.data.get('business', None)
    vendor_id = request.data.get('vendor', None)
    category_id = request.data.get('category', None)
    brand_id = request.data.get('brand', None)
    product_type = request.data.get('product_type', None)
    name = request.data.get('name', None)
    cost_price = request.data.get('cost_price', None)
    full_price = request.data.get('full_price', None)
    sell_price = request.data.get('sell_price', None)
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
    stock_status = request.data.get('stock_status', True)
    alert_when_stock_becomes_lowest = request.data.get('alert_when_stock_becomes_lowest', True)



    if not all([name, business_id, medias, vendor_id, category_id, brand_id, product_type, cost_price, full_price, sell_price, short_description, description, barcode_id, sku, quantity, unit, amount, alert_when_stock_becomes_lowest]):
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
        vendor = BusinessAddress.objects.get(id=vendor_id, is_deleted=False, is_active=True)
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
        short_description = short_description,
        description = description,
        barcode_id = barcode_id,
        sku = sku,
        slug = str(name).replace(' ' , '-').replace('/' , '-').replace('?' , '-'),
        is_active=True,
        published = True,
    )
    for med in medias:
        ProductMedia.objects.create(
            user=user,
            business=business,
            product=product,
            image=med
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

    serialized = ProductSerializer(product)
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