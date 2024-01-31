from .models import SaleRecords
from Invoices.models import SaleInvoice
from django.db.models import Q


def matching_records(location=None, range_start=None, range_end=None, services=None, client=None , search_text = None):
    try:
        filters = Q()

        if location is not None:
            filters &= Q(location_id=location)

        if range_start is not None:
            filters &= Q(date__gte=range_start)

        if range_end is not None:
            filters &= Q(date__lte=range_end)

        if services is not None:
            filters &= Q(services=services)

        if client is not None:
            filters &= Q(client=client)
            
        if search_text is not None:
            search_text = search_text.replace('#', '')
            invoice_checkout_ids = list(
                SaleInvoice.objects.filter(id__icontains=search_text).values_list('checkout', flat=True))
            sale_queries &= Q(id__in=invoice_checkout_ids) | Q(client__full_name__icontains=search_text)
            app_queries &= Q(id__in=invoice_checkout_ids) | Q(appointment__client__full_name__icontains=search_text)

        # Fetch records based on the constructed filters
            matching_records = SaleRecords.objects.filter(filters)
        else:
            matching_records = SaleRecords.objects.all()
        
        return matching_records
        
    except Exception as e:
        
        raise ValueError(f"Error processing matching_records: {str(e)}")