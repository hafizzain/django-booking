from django import template
register = template.Library()

from Order.models import ServiceOrder, ProductOrder
from MultiLanguage.models import InvoiceTranslation


@register.simple_tag
def get_translation(order_id):
    service_order = ServiceOrder.objects.filter(id=order_id).first()
    product_order = ProductOrder.objects.filter(id=order_id).first()

    if service_order and service_order.location.secondary_translation:
        secondary_invoice_traslation = InvoiceTranslation.objects.filter(id=service_order.location.secondary_translation.id).first()
        translation = service_order.service.servicetranlations_set.get(language__id=secondary_invoice_traslation.language.id)
        return translation.service_name
    
    if product_order and product_order.location.secondary_translation:
        secondary_invoice_traslation = InvoiceTranslation.objects.filter(id=product_order.location.secondary_translation.id).first()
        translation = product_order.product.producttranslations_set.get(language__id=secondary_invoice_traslation.language.id)
        return translation.service_name
    
    return ''