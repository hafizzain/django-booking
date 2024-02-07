from django import template
register = template.Library()

from Order.models import ServiceOrder, ProductOrder
from MultiLanguage.models import InvoiceTranslation
from Appointment.models import AppointmentService
from SaleRecords.models import *


@register.simple_tag
def get_secondary_translation(order_id):
    try:
        
        service_order = SaleRecordServices.objects.filter(id=order_id).first()
        product_order = SaleRecordsProducts.objects.filter(id=order_id).first()
        appointment_order = SaleRecordsAppointmentServices.objects.filter(id=order_id).first()

        if service_order and service_order.sale_record.location.secondary_translation:
            secondary_invoice_traslation = InvoiceTranslation.objects.filter(id=service_order.sale_record.location.secondary_translation.id).first()
            translation = service_order.service.servicetranlations_set.filter(language__id=secondary_invoice_traslation.language.id).first()
            return translation.service_name if translation else ''
        
        if product_order and product_order.sale_record.location.secondary_translation:
            secondary_invoice_traslation = InvoiceTranslation.objects.filter(id=product_order.sale_record.location.secondary_translation.id).first()
            translation = product_order.product.producttranslations_set.filter(language__id=secondary_invoice_traslation.language.id).first()
            return translation.product_name if translation else ''
        
        if appointment_order and appointment_order.sale_record.location.secondary_translation:
            secondary_invoice_traslation = InvoiceTranslation.objects.filter(id=appointment_order.sale_record.location.secondary_translation.id).first()
            translation = appointment_order.service.servicetranlations_set.filter(language__id=secondary_invoice_traslation.language.id).first()
            return translation.service_name if translation else ''
        
        return ''
    except Exception as e:
        return f"exception occure in secondary translation : {str(e)}"

@register.simple_tag
def get_primary_translation(order_id):
    try:
        service_order = SaleRecordServices.objects.filter(id=order_id).first()
        product_order = SaleRecordsProducts.objects.filter(id=order_id).first()
        appointment_order = SaleRecordsAppointmentServices.objects.filter(id=order_id).first()

        if service_order and service_order.sale_record.location.primary_translation:
            primary_invoice_traslation = InvoiceTranslation.objects.filter(id=service_order.sale_record.location.primary_translation.id).first()
            translation = service_order.service.servicetranlations_set.filter(language__id=primary_invoice_traslation.language.id).first()
            return translation.service_name if translation else ''
        
        if product_order and product_order.sale_record.location.primary_translation:
            primary_invoice_traslation = InvoiceTranslation.objects.filter(id=product_order.sale_record.location.primary_translation.id).first()
            translation = product_order.product.producttranslations_set.filter(language__id=primary_invoice_traslation.language.id).first()
            return translation.product_name if translation else ''
        

        """
        Appointment Services have no invoice translation implemented.
        We just need to show the primary name which is as follows:
        """
        if appointment_order:
            return appointment_order.service.name

        
        return ''
    except Exception as e:
        return f"exception occure in primary translation : {str(e)}"