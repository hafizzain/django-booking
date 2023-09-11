from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings

from django_tenants.utils import tenant_context

from Sale.serializers import SaleOrders_CheckoutSerializer



def send_order_email(client, checkout_order, request):
    
    with tenant_context(request.tenant):

        order_data = dict(SaleOrders_CheckoutSerializer(checkout_order, context={'request':request}).data)
        
        #Summary
        total_tax = order_data['gst_price'] + order_data['gst_price1']
        created_at = order_data['created_at']
        locatiion = order_data['location']['address_name']
        client_name = order_data['client']['full_name']
        payment_method = order_data['payment_type']
        total_tip = order_data['invoice']['tip']

        sub_total = 0
        for key, value in order_data.items():
            if key in ['product', 'membership', 'voucher', 'service']:
                _item_total = sum([a['price'] * a['quantity'] for a in value])
                sub_total += _item_total

        total_amount = sub_total + total_tax + total_tip

        html_file = render_to_string('ClientOrderMail/client_order_email.html',
                                    {
                                        'created_at': created_at,
                                        'locatiion': locatiion,
                                        'client_name': client_name,
                                        'payment_method': payment_method,
                                        'total_tax': total_tax,
                                        'total_tip': total_tip,
                                        'sub_total': sub_total,
                                        'total_amount': total_amount

                                    })
        text_content = strip_tags(html_file)


        email = EmailMultiAlternatives(
                'New Order',
                text_content,
                settings.EMAIL_HOST_USER,
                to = [client.email],
            )
        
        email.attach_alternative(html_file, "text/html")
        email.send()