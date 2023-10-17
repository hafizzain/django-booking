from django import template
register = template.Library()

from Order.models import ServiceOrder, ProductOrder
from MultiLanguage.models import InvoiceTranslation


@register.simple_tag
def get_secondary_translation(order_id):
    service_order = ServiceOrder.objects.filter(id=order_id).first()
    product_order = ProductOrder.objects.filter(id=order_id).first()

    if service_order and service_order.location.secondary_translation:
        secondary_invoice_traslation = InvoiceTranslation.objects.filter(id=service_order.location.secondary_translation.id).first()
        translation = service_order.service.servicetranlations_set.filter(language__id=secondary_invoice_traslation.language.id).first()
        return translation.service_name if translation else ''
    
    if product_order and product_order.location.secondary_translation:
        secondary_invoice_traslation = InvoiceTranslation.objects.filter(id=product_order.location.secondary_translation.id).first()
        translation = product_order.product.producttranslations_set.filter(language__id=secondary_invoice_traslation.language.id).first()
        return translation.product_name if translation else ''
    
    return ''

@register.simple_tag
def get_primary_translation(order_id):
    service_order = ServiceOrder.objects.filter(id=order_id).first()
    product_order = ProductOrder.objects.filter(id=order_id).first()

    if service_order and service_order.location.primary_translation:
        secondary_invoice_traslation = InvoiceTranslation.objects.filter(id=service_order.location.primary_translation.id).first()
        translation = service_order.service.servicetranlations_set.filter(language__id=secondary_invoice_traslation.language.id).first()
        return translation.service_name if translation else ''
    
    if product_order and product_order.location.primary_translation:
        secondary_invoice_traslation = InvoiceTranslation.objects.filter(id=product_order.location.primary_translation.id).first()
        translation = product_order.product.producttranslations_set.filter(language__id=secondary_invoice_traslation.language.id).first()
        return translation.product_name if translation else ''
    
    return ''