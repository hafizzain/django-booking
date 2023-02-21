
from Product.models import ProductStock


def ReorderQunatity():
    product_stock = ProductStock.objects.filter(product__is_active = True, is_deleted = False)
    for stock in product_stock:
        sold = int(stock.sold_quantity) + int(stock.consumed_quantity) 
        rem = int(stock.reorder_quantity) - sold
        if rem  > 0:
            stock.reorder_quantity += rem
            stock.low_stock += rem
            stock.save()
        