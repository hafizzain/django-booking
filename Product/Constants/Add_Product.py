from Utility.models import ExceptionRecord

def add_product_remaing(**kwargs):
    for product, value in kwargs.items():
           # print(f" {product}, {value}")
        ProductStock.objects.create(
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