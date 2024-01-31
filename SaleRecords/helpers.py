from .models import SaleRecords
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

        # Fetch records based on the constructed filters
        matching_records = SaleRecords.objects.filter(filters)
        return matching_records
        
    except Exception as e:
        
        raise ValueError(f"Error processing matching_records: {str(e)}")