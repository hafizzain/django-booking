from .models import SaleRecords
from django.db.models import Q
from Client.models import LoyaltyPoints, LoyaltyPointLogs, ClientLoyaltyPoint

def matching_records(is_quick_sale = None,location=None, range_start=None, range_end=None, services=None, client=None , search_text = None):
    try:
        filters = Q()

        if location is not None:
            filters &= Q(location_id=location)

        if range_start is not None:
            filters &= Q(created_at__gte=range_start)

        if range_end is not None:
            filters &= Q(created_at__lte=range_end)

        if services is not None:
            filters &= Q(services=services)

        if client is not None:
            filters &= Q(client=client)
        
        if is_quick_sale:
            matching_records = SaleRecords.objects.filter(filters).order_by('-created_at')[:5]
            return matching_records
        else:
            # Fetch records based on the constructed filters
            matching_records = SaleRecords.objects.filter(filters).order_by('-created_at')
            return matching_records
        
    except Exception as e:
        
        raise ValueError(f"Error processing matching_records: {str(e)}")
    
    
def calculate_voucher_commission(voucher = []):
    pass


def calculate_loyalty_points(client_bill, amount_spent, points_per_amount, every_point, reward_amount_per_point):
    """
    Calculate loyalty points and the corresponding reward amount.

    Parameters:
    - amount_spent: The total amount spent by the client.
    - points_per_amount: The number of loyalty points awarded per unit of currency spent.
    - reward_amount_per_point: The reward amount for each loyalty point.

    Returns:
    A tuple containing the total loyalty points and the corresponding reward amount.
    """
    
    amount_for_calcluating_point = client_bill/amount_spent
    eard_points = amount_for_calcluating_point*points_per_amount
    wallet_reward_amount = reward_amount_per_point * every_point
    
    
    

    return amount_for_calcluating_point, eard_points, wallet_reward_amount


