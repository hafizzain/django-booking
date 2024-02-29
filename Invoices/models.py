from datetime import datetime
from django.db import models
from django.utils.timezone import now
from Authentication.models import User
from Client.models import Client, LoyaltyPointLogs
from Employee.models import Employee
from Business.models import BusinessAddress
from uuid import uuid4
from Appointment.models import Appointment
import pdfkit
from django.conf import settings
from django.template.loader import get_template
import os
from django.db import connection
from django.db.models import F, Q
from Order.models import Order, Checkout, ProductOrder, ServiceOrder, VoucherOrder, MemberShipOrder
from Appointment.models import Appointment, AppointmentCheckout, AppointmentService, AppointmentEmployeeTip
from Utility.models import ExceptionRecord
from MultiLanguage.models import InvoiceTranslation
from MultiLanguage.serializers import InvoiceTransSerializer
# from Utility.get_models import get_sale_record_model
# from SaleRecords.models import *


class SaleInvoice(models.Model):
    status_choice=[
        ('Completed', 'Completed'),
        ('Incompleted', 'Incompleted'),
        ('Expired', 'Expired'),
        ('Active', 'Active'),        
    ]
    
    CLIENT_TYPE=[
        ('Walk_in', 'Walk-in'),
        ('In_Saloon', 'In-Saloon'),
    ]
    PAYMENT_TYPE=[
        ('Cash', 'Cash'),
        ('Voucher', 'Voucher'),
        ('SplitBill', 'SplitBill'),
        ('MasterCard', 'MasterCard'),
        ('Other', 'Other'),
        
    ]
    
    CHECKOUT_TYPE = [
        ('sale','Sale'),
        ('appointment', 'Appointment'),
        ('refund','refund')
    ]
    
    INVOICE_TYPE = [
        ('refund', 'Refund'),
        ('order','Order'),
    ]
    
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, null=True, blank=True)
    # member = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, related_name = 'member_records')
    
    # employee = models.ForeignKey(Employee, on_delete = models.CASCADE,blank=True, null=True, related_name = 'employee_records')
    
    client_type = models.CharField(choices = CLIENT_TYPE, max_length=50 , default = '', null=True, blank=True )
    payment_type = models.CharField(choices = PAYMENT_TYPE, max_length=50 , default = '', null=True, blank=True )
    # tip = models.FloatField(default = 0)
    # total_service_price = models.FloatField(default = 0 , null=True, blank=True)
    # total_product_price = models.FloatField(default = 0 , null=True, blank=True)
    # total_voucher_price = models.FloatField(default = 0 , null=True, blank=True)
    # total_membership_price = models.FloatField(default = 0 , null=True, blank=True)
    
    # service_commission = models.FloatField(default = 0 , null=True, blank=True)
    # product_commission = models.FloatField(default = 0 , null=True, blank=True)
    # voucher_commission = models.FloatField(default = 0 , null=True, blank=True)
    
    # service_commission_type = models.CharField( max_length=50 , default = '', null=True, blank=True)
    # product_commission_type = models.CharField( max_length=50 , default = '', null=True, blank=True)
    # voucher_commission_type = models.CharField( max_length=50 , default = '', null=True, blank=True)
    
    # is_promotion = models.BooleanField(default=False)
    # selected_promotion_id = models.CharField(default='', max_length=800, null=True, blank=True)
    # selected_promotion_type = models.CharField(default='', max_length=400, null=True, blank=True)
    
    # appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True) # will not use this 
    # appointment_service = models.CharField(max_length=2000, default='', null=True, blank=True) # will not use this 
    # service = models.CharField(max_length=2000, default='', null=True, blank=True) # will not
    member = models.CharField(blank=True, default='', max_length=2000, null=True)
    # business_address = models.CharField(max_length=2000, default='', null=True, blank=True)
    
    # types of checkout and invoices
    
    invoice_type = models.CharField(choices = INVOICE_TYPE, max_length=50 , default = '', null=True, blank=True )
    checkout_type = models.CharField(choices = CHECKOUT_TYPE, max_length=50 , default = '', null=True, blank=True )
    
    # ================================== New Fields =========================
    sub_total = models.FloatField(default=0, null=True, blank=True)
    change = models.FloatField(default = 0 , blank=True, null=True)
    total_amount = models.FloatField(default=0, null=True, blank=True)
    total_tax = models.FloatField(default=0, null=True, blank=True)
    total_tip = models.FloatField(default=0, null=True, blank=True)
    
    # gst = models.FloatField(default=0, null=True, blank=True)
    # gst_price = models.FloatField(default=0, null=True, blank=True)
    
    # gst = models.FloatField(default=0, null=True, blank=True) # will not use
    # gst_price = models.FloatField(default=0, null=True, blank=True) # will not use
    
    # service_price = models.FloatField(default=0, null=True, blank=True) # Will not use
    # total_price = models.FloatField(default=0, null=True, blank=True) # will not use
    checkout = models.CharField(max_length=128, null=True, blank=True)

    file = models.FileField(upload_to='invoicesFiles/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    
    def __str__(self):
        return str(self.id)
    
    @property
    def checkout_instance(self):
        from SaleRecords.models import SaleRecords
        '''
        getting the checkout instance of the checkout based on the checkout_type from the invoice model
        '''
        # if self.checkout_type == 'appointment':
        #     checkout_instance = AppointmentCheckout.objects.get(id=self.checkout)
        # else:
        #     checkout_instance = Checkout.objects.get(id=self.checkout)
        
        # return checkout_instance
        checkout_instance = SaleRecords.objects.get(id = self.checkout)
        return checkout_instance
    
    @property
    def short_id(self):
        uuid = f'{self.id}'
        uuid = uuid.split('-')[0]
        return uuid
    
    # def get_appointment_services(self, app_checkout):
    #     # old
    #     # services = AppointmentService.objects.filter(
    #     #     appointment = app_checkout.appointment
    #     # )
    #     # New Query
    #     appointment_services = SaleRecordsAppointmentServices.objects.filter(sale_record = app_checkout)
    #     ordersData = []
    #     for data in appointment_services:
    #         # price = order.get_final_price() -> old
    #         data = {
    #             'id': data.service.id,
    #             'name' : f'{data.service.name}',
    #             'arabic_name' : f'{data.service.arabic_name}',
    #             # 'price' : round(price, 2), old
    #             'price': data.price,
    #             'quantity' : 1
    #         }
    #         ordersData.append(data)
    #     return ordersData

    # def get_order_items(self, checkout):
    #     orders = []
        
    #     # ================================================ Old ===============================
    #     orders.extend(ProductOrder.objects.filter(checkout = checkout).annotate(name = F('product__name'), arabic_name=F('product__arabic_name')))
    #     # orders.extend(ServiceOrder.objects.filter(checkout = checkout).annotate(name = F('service__name'), arabic_name=F('service__arabic_name')))
    #     # orders.extend(VoucherOrder.objects.filter(checkout = checkout).annotate(name = F('voucher__name'), arabic_name=F('voucher__arabic_name')))
    #     # orders.extend(MemberShipOrder.objects.filter(checkout = checkout).annotate(name = F('membership__name'), arabic_name=F('membership__arabic_name')))
        
    #     order.extend(SaleRecordsProducts.objects.filter(sale_record = checkout).annotate(name = F('product__name'), arabic_name=F('product__arabic_name')))
    #     order.extend(SaleRecordServices.objects.filter(sale_record = checkout).annotate(name = F('service__name'), arabic_name=F('service__arabic_name')))
    #     order.extend(SaleRecordMembership.objects.filter(sale_record = checkout).annotate(name = F('membership__name'), arabic_name=F('membership__arabic_name')))
    #     order.extend(SaleRecordVouchers.objects.filter(sale_record = checkout).annotate(name = F('voucher__name'), arabic_name=F('voucher__arabic_name')))

    #     ordersData = []
    #     for order in orders:
    #         # pricing order for invoice PDF

    #         #region debugging
    #         price = None
    #         if order.is_redeemed == True:
    #             price = order.redeemed_price
    #         elif order.discount_price is not None:
    #             price = order.discount_price
    #         else:
    #             price = order.current_price
            
    #         # will remove this code after debugging
    #         # price = order.redeemed_price or order.discount_price or order.total_price
            
    #         total_price = float(price) * float(order.quantity)
    #         #endregion

    #         data = {
    #             'id': order.id,
    #             'name' : f'{order.name}',
    #             'arabic_name' : f'{order.arabic_name}',
    #             'price' : round(total_price, 2),
    #             'quantity' : order.quantity,
    #             'discount_percentage': int(order.discount_percentage) if order.discount_percentage else None,
    #         }

    #         ordersData.append(data)

    #     return ordersData

    # def get_invoice_order_items(self):
    #     try:
    #         checkout = Checkout.objects.get(
    #             id = self.checkout
    #         )
    #         return [
    #                 self.get_order_items(checkout), 
    #                 self.get_tips(checkout_type='Checkout', id=self.checkout), 
    #                 {
    #                     'tax_applied' : round(checkout.tax_applied, 2),
    #                     'tax_amount' : round(checkout.tax_amount, 2),
    #                     'tax_applied1' : round(checkout.tax_applied1, 2),
    #                     'tax_amount1' : round(checkout.tax_amount1, 2),
    #                     'tax_name': checkout.tax_name,
    #                     'tax_name1': checkout.tax_name1
    #                 }
    #             ]
    #     except Exception as err:
    #         ExceptionRecord.objects.create(
    #             text = f'Sale INVOICE ERROR not found {str(err)} -- {self.checkout}'
    #         )
    #         try:
    #             checkout = AppointmentCheckout.objects.get(
    #                 id = self.checkout
    #             )
    #             return [
    #                     self.get_appointment_services(checkout), 
    #                     self.get_tips(checkout_type='Appointment', id=f'{checkout.appointment.id}'),
    #                     {
    #                         'tax_applied' : round(checkout.gst, 2),
    #                         'tax_amount' : round(checkout.gst_price, 2),
    #                         'tax_applied1' : round(checkout.gst1, 2),
    #                         'tax_amount1' : round(checkout.gst_price1, 2),
    #                         'tax_name': checkout.tax_name,
    #                         'tax_name1': checkout.tax_name1
    #                     }
    #                 ]
    #         except Exception as err:
    #             ExceptionRecord.objects.create(
    #                 text = f'Sale INVOICE ERROR not found {str(err)} -- {self.checkout}'
    #             )
    #     return [[], [], {}]

    # def get_tips(self, checkout_type = None, id=None):
    #     if not checkout_type or not id:
    #         return []
    #     query = {}

    #     if checkout_type == 'Appointment':
    #         query['appointment__id'] = id
    #     else:
    #         query['checkout__id'] = id
        
    #     tips = AppointmentEmployeeTip.objects.filter(**query)
    #     tips = [{'tip' : round(tip.tip, 2), 'employee_name' : tip.member.full_name} for tip in tips]
    #     return tips
    def get_all_order_items (self):
        from SaleRecords.models import SaleRecords
        try:
            sale_records = SaleRecords.objects.get(id = self.checkout)
            
            if sale_records.checkout_type == "Appointment" or sale_records.checkout_type == "Group Appointment":
                clients = sale_records.appointment_services.values_list('client', flat = True).distinct()
                raise ValueError(f"{clients.count()}")
                return sale_records, clients
            
            return sale_records, None
        except Exception as e:
            return None, f"{e}"
    
    
    def save(self, *args, **kwargs):
        if not self.file and self.checkout:
            # order_items, order_tips, tax_details = self.get_invoice_order_items()
            # if len(order_items) > 0:
            #     sub_total = sum([order['price'] for order in order_items])
            #     tips_total = sum([t['tip'] for t in order_tips])

                # checkout_redeem_data = self.get_checkout_redeemed_data()
                # coupon_data = self.get_checkout_coupon_data()
                
                checkout_data, clients = self.get_all_order_items()

                context = {
                    'client': self.client,
                    'invoice_by' : self.user.user_full_name if self.user else '',
                    'invoice_by_arabic_name' : self.user.user_full_name if self.user else '',
                    'invoice_id' : self.short_id,
                    # 'order_items' : order_items,
                    'currency_code' : self.location.currency.code,
                    # 'sub_total' : round(sub_total, 2),
                    'sub_total': self.sub_total,
                    # 'tips' : order_tips,
                    # 'tips':
                    'total_tip':self.total_tip,
                    'change': self.change,
                    # 'total' : round((float(tips_total) + float(sub_total) + float(tax_details.get('tax_amount', 0)) + float(tax_details.get('tax_amount1', 0))), 2),
                    'total': self.total_amount,
                    'created_at' : datetime.now(),
                    'BACKEND_HOST' : settings.BACKEND_HOST,
                    'payment_type': self.payment_type,
                    'location':self.location.address_name,
                    'business_address':self.location,
                    'tax': self.total_tax,
                    'checkout_data':checkout_data,
                    'clients': clients,
                    # 'redeemed_points':self.get_client_loyalty_points(),
                    # 'coupon_data':coupon_data,
                    # **tax_details,
                    # **checkout_redeem_data,
                }
                schema_name = connection.schema_name
                schema_dir = f'{settings.BASE_DIR}/media/{schema_name}'
                is_schema_dir_exist = os.path.isdir(schema_dir)
                if not is_schema_dir_exist:
                    os.mkdir(schema_dir)

                output_dir = f'{settings.BASE_DIR}/media/{schema_name}/invoicesFiles'
                is_exist = os.path.isdir(output_dir)
                if not is_exist:
                    os.mkdir(output_dir)

                file_name = f'invoice-{self.short_id}.pdf'
                output_path = f'{output_dir}/{file_name}'
                no_media_path = f'invoicesFiles/{file_name}'
                # template = get_template(f'{settings.BASE_DIR}/templates/Sales/invoice.html')
                template = get_template(f'{settings.BASE_DIR}/templates/Sales/invoice_3.html') # New Design for Invoice file
                html_string = template.render(context)
                pdfkit.from_string(html_string, os.path.join(output_path))
                self.file = no_media_path

        super(SaleInvoice, self).save(*args, **kwargs)

    # def get_checkout_redeemed_data(self):

    #     data = dict()

    #     checkout = Checkout.objects.filter(
    #         id=self.checkout
    #     ).first()

    #     if checkout:
    #         data['redeem_option'] = checkout.redeem_option
    #         data['total_discount'] = checkout.total_discount
    #         data['voucher_redeem_percentage'] = checkout.voucher_redeem_percentage

    #     return data

    # def get_checkout_coupon_data(self):

    #     data = dict()
    #     try:
    #         checkout = Checkout.objects.get(
    #             id=self.checkout
    #         )
    #         if checkout:
    #             data['is_coupon_redeemed'] = checkout.is_coupon_redeemed
    #             data['coupon_discounted_price'] = checkout.coupon_discounted_price
    #         return data
    #     except:
    #         checkout = AppointmentCheckout.objects.get(
    #             id=self.checkout
    #         )
    #         if checkout:
    #             data['is_coupon_redeemed'] = checkout.is_coupon_redeemed
    #             data['coupon_discounted_price'] = checkout.coupon_discounted_price
    #         return data
    
    # def get_client_loyalty_points(self):
    #     if self.client:
    #         redeemed_points_obj_count = LoyaltyPointLogs.objects.filter(client=self.client,
    #                                                           location=self.location).count()
    #         if redeemed_points_obj_count > 0:
    #             redeemed_points_obj = LoyaltyPointLogs.objects.filter(client=self.client, location=self.location) \
    #                                                         .order_by('-created_at')[0]
    #             return redeemed_points_obj.points_redeemed
    #         else:
    #             return None 
    #     else:
    #         return None


