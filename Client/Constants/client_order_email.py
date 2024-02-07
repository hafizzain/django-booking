from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings

from django_tenants.utils import tenant_context

from Business.models import AdminNotificationSetting, ClientNotificationSetting

from Sale.serializers import SaleOrders_CheckoutSerializer



def send_order_email(checkout, request):
    
    with tenant_context(request.tenant):
        
        emails = []
        client_email = ClientNotificationSetting.objects.get(business=str(checkout.location.business))
        admin_email = AdminNotificationSetting.objects.get(business=str(checkout.location.business))

        if admin_email.email_notify_on_appoinment or admin_email.sms_notify_on_quick_sale:
            emails.append(request.user.email)

        if client_email.sms_appoinment:
            emails.append(checkout.client.email)
        order_data = dict(SaleOrders_CheckoutSerializer(checkout, context={'request':request}).data)
        
        #Summary
        total_tax = round(float(order_data['gst_price']) + float(order_data['gst_price1']), 2)
        created_at = order_data['created_at']
        location = order_data['location']['address_name']
        payment_method = order_data['payment_type']

        total_tip = 0
        sub_total = 0

        for key, value in order_data.items():

            if key in ['product', 'membership', 'service']:
                _item_total = sum([a['price'] * a['quantity'] for a in value])
                sub_total += _item_total

            if key == 'voucher':
                _item_total = sum([a['voucher_price'] * a['quantity'] for a in value])
                sub_total += _item_total

            if key == 'tip':
                total_tip += sum([tip['tip'] for tip in value])

        total_amount = sub_total + total_tax + total_tip

        html_file = render_to_string('ClientOrderMail/client_order_email.html',
                                    {
                                        'created_at': created_at,
                                        'location': location,
                                        'client_name': checkout.client.full_name,
                                        'payment_method': payment_method,
                                        'total_tax': total_tax,
                                        'total_tip': total_tip,
                                        'sub_total': sub_total,
                                        'total_amount': total_amount

                                    })
        text_content = strip_tags(html_file)


        email = EmailMultiAlternatives(
                'Exclusive Quick Sale Alert',
                text_content,
                settings.EMAIL_HOST_USER,
                to = emails,
            )
        
        email.attach_alternative(html_file, "text/html")
        email.send()


def send_membership_order_email(membership_order, business_address, request):
    
    with tenant_context(request.tenant):

        membership_currency = membership_order.membership.membership_currenypricemembership.filter(currency=business_address.currency).first()
        html_file = render_to_string('ClientOrderMail/membership_sale_order.html',
                                     {'membership_order':membership_order,
                                      'membership_currency':membership_currency,
                                      'location':business_address
                                      }
                                    )
        text_content = strip_tags(html_file)


        email = EmailMultiAlternatives(
                'Membership Sale Alert',
                text_content,
                settings.EMAIL_HOST_USER,
                to = [membership_order.sale_record.client.email],
            )
        
        email.attach_alternative(html_file, "text/html")
        email.send()