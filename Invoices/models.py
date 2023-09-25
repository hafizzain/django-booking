from datetime import datetime
from django.db import models
from django.utils.timezone import now
from Authentication.models import User
from Client.models import Client
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
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, null=True, blank=True)
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    client_type = models.CharField(choices = CLIENT_TYPE, max_length=50 , default = '', null=True, blank=True )
    payment_type = models.CharField(choices = PAYMENT_TYPE, max_length=50 , default = '', null=True, blank=True )
    tip = models.FloatField(default = 0)
    total_service_price = models.FloatField(default = 0 , null=True, blank=True)
    total_product_price = models.FloatField(default = 0 , null=True, blank=True)
    total_voucher_price = models.FloatField(default = 0 , null=True, blank=True)
    total_membership_price = models.FloatField(default = 0 , null=True, blank=True)
    
    service_commission = models.FloatField(default = 0 , null=True, blank=True)
    product_commission = models.FloatField(default = 0 , null=True, blank=True)
    voucher_commission = models.FloatField(default = 0 , null=True, blank=True)
    
    service_commission_type = models.CharField( max_length=50 , default = '', null=True, blank=True)
    product_commission_type = models.CharField( max_length=50 , default = '', null=True, blank=True)
    voucher_commission_type = models.CharField( max_length=50 , default = '', null=True, blank=True)
    
    is_promotion = models.BooleanField(default=False)
    selected_promotion_id = models.CharField(default='', max_length=800, null=True, blank=True)
    selected_promotion_type = models.CharField(default='', max_length=400, null=True, blank=True)
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    appointment_service = models.CharField(max_length=2000, default='', null=True, blank=True)
    service = models.CharField(max_length=2000, default='', null=True, blank=True)
    member = models.CharField(max_length=2000, default='', null=True, blank=True)
    business_address = models.CharField(max_length=2000, default='', null=True, blank=True)

    gst = models.FloatField(default=0, null=True, blank=True)
    gst_price = models.FloatField(default=0, null=True, blank=True)
    
    service_price = models.FloatField(default=0, null=True, blank=True)
    total_price = models.FloatField(default=0, null=True, blank=True)
    checkout = models.CharField(max_length=128, null=True, blank=True)
    checkout_obj = models.OneToOneField(Checkout, null=True, blank=True, on_delete=models.CASCADE, related_name='invoice')

    file = models.FileField(upload_to='invoicesFiles/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return str(self.id)
    
    @property
    def short_id(self):
        uuid = f'{self.id}'
        uuid = uuid.split('-')[0]
        return uuid
    
    def get_appointment_services(self, app_checkout):
        services = AppointmentService.objects.filter(
            appointment = app_checkout.appointment
        )
        ordersData = []
        for order in services:
            price = order.get_final_price()
            data = {
                'name' : f'{order.service.name}',
                'arabic_name' : f'{order.service.arabic_name}',
                'price' : round(price, 2),
                'quantity' : 1
            }
            ordersData.append(data)
        return ordersData

    def get_order_items(self, checkout):
        orders = []

        orders.extend(ProductOrder.objects.filter(checkout = checkout).annotate(name = F('product__name'), arabic_name=F('product__arabic_name')))
        orders.extend(ServiceOrder.objects.filter(checkout = checkout).annotate(name = F('service__name'), arabic_name=F('service__arabic_name')))
        orders.extend(VoucherOrder.objects.filter(checkout = checkout).annotate(name = F('voucher__name'), arabic_name=F('voucher__arabic_name')))
        orders.extend(MemberShipOrder.objects.filter(checkout = checkout).annotate(name = F('membership__name'), arabic_name=F('membership__arabic_name')))

        ordersData = []
        for order in orders:
            # pricing order for invoice PDF

            #region debugging
            price = None
            if order.is_redeemed == True:
                price = order.redeemed_price
            elif order.discount_price is not None:
                price = order.discount_price
            else:
                price = order.current_price
            
            # will remove this code after debugging
            # price = order.redeemed_price or order.discount_price or order.total_price
            
            total_price = float(price) * float(order.quantity)
            #endregion

            data = {
                'name' : f'{order.name}',
                'arabic_name' : f'{order.arabic_name}',
                'price' : round(total_price, 2),
                'quantity' : order.quantity,
                'discount_percentage':order.discount_percentage,
            }
            ordersData.append(data)

        return ordersData

    def get_invoice_order_items(self):
        try:
            checkout = Checkout.objects.get(
                id = self.checkout
            )
            return [
                    self.get_order_items(checkout), 
                    self.get_tips(checkout_type='Checkout', id=self.checkout), 
                    {
                        'tax_applied' : round(checkout.tax_applied, 2),
                        'tax_amount' : round(checkout.tax_amount, 2),
                        'tax_applied1' : round(checkout.tax_applied1, 2),
                        'tax_amount1' : round(checkout.tax_amount1, 2),
                        'tax_name': checkout.tax_name,
                        'tax_name1': checkout.tax_name1
                    }
                ]
        except Exception as err:
            ExceptionRecord.objects.create(
                text = f'Sale INVOICE ERROR not found {str(err)} -- {self.checkout}'
            )
            try:
                checkout = AppointmentCheckout.objects.get(
                    id = self.checkout
                )
                return [
                        self.get_appointment_services(checkout), 
                        self.get_tips(checkout_type='Appointment', id=f'{checkout.appointment.id}'),
                        {
                            'tax_applied' : round(checkout.gst, 2),
                            'tax_amount' : round(checkout.gst_price, 2),
                            'tax_applied1' : round(checkout.gst1, 2),
                            'tax_amount1' : round(checkout.gst_price1, 2),
                            'tax_name': checkout.tax_name,
                            'tax_name1': checkout.tax_name1
                        }
                    ]
            except Exception as err:
                ExceptionRecord.objects.create(
                    text = f'Sale INVOICE ERROR not found {str(err)} -- {self.checkout}'
                )
        return [[], [], {}]

    def get_tips(self, checkout_type = None, id=None):
        if not checkout_type or not id:
            return []
        query = {}

        if checkout_type == 'Appointment':
            query['appointment__id'] = id
        else:
            query['checkout__id'] = id
        
        tips = AppointmentEmployeeTip.objects.filter(**query)
        tips = [{'tip' : round(tip.tip, 2), 'employee_name' : tip.member.full_name} for tip in tips]
        return tips
    
    def save(self, *args, **kwargs):
        if not self.file and self.checkout:
            order_items, order_tips, tax_details = self.get_invoice_order_items()
            invoice_trans = self.get_invoice_translations()
            if len(order_items) > 0:
                sub_total = sum([order['price'] for order in order_items])
                tips_total = sum([t['tip'] for t in order_tips])

                context = {
                    'client': self.client,
                    'invoice_by' : self.user.user_full_name if self.user else '',
                    'invoice_by_arabic_name' : self.user.user_full_name if self.user else '',
                    'invoice_id' : self.short_id,
                    'order_items' : order_items,
                    'currency_code' : self.location.currency.code,
                    'sub_total' : round(sub_total, 2),
                    'tips' : order_tips,
                    'total' : round((float(tips_total) + float(sub_total) + float(tax_details.get('tax_amount', 0)) + float(tax_details.get('tax_amount1', 0))), 2),
                    'created_at' : datetime.now().strftime('%Y-%m-%d'),
                    'BACKEND_HOST' : settings.BACKEND_HOST,
                    'invoice_trans': invoice_trans['invoice'] if invoice_trans else '',
                    'items_trans': invoice_trans['items'] if invoice_trans else '',
                    'amount_trans': invoice_trans['amount'] if invoice_trans else '',
                    'subtotal_trans': invoice_trans['subtotal'] if invoice_trans else '',
                    'total_trans': invoice_trans['total'] if invoice_trans else '',
                    'payment_type_trans': invoice_trans['payment_method'] if invoice_trans else '',
                    'payment_type': self.payment_type,
                    **tax_details,
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

    def get_invoice_translations(self):
        """
        This function will return the invoice translation object
        based on the invoice business address / location. That 
        translation will then embed into invoice template.
        """
        if self.location:
            invoice_trans = InvoiceTranslation.objects.filter(
                status= 'active',
                location=self.location
            ).first()

            translation_data = InvoiceTransSerializer(invoice_trans).data
            return dict(translation_data)
        else:
            return None

