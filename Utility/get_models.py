from importlib import import_module

# from SaleRecords.models import PaymentMethods

def get_payment_method_module():
    PaymentMethods = import_module('SaleRecords.models').PaymentMethods
    return PaymentMethods

def get_sale_record_model(): 
    sale_record = import_module('SaleRecords.models').SaleRecords
    return sale_record