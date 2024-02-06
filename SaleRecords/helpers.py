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

    
def loyalty_points_update(location = None, client= None, loyalty_points = None , sub_total = None, sale_record = None, invoice = None ):
        try:
            if location and loyalty_points and sub_total and client:
                redeemed_loyalty = loyalty_points[0]
                client_points = ClientLoyaltyPoint.objects.get(id=redeemed_loyalty['clinet_loyalty_point'])
                
                client_points.points_redeemed = float(client_points.points_redeemed) + float(redeemed_loyalty['redeemed_points'])
                client_points.save()

                single_point_value = client_points.customer_will_get_amount / client_points.for_every_points
                total_redeemed_value = float(single_point_value) * float(redeemed_loyalty['redeemed_points'])

                logs_points_redeemed = redeemed_loyalty['redeemed_points']
                logs_total_redeened_value = total_redeemed_value
                
                location_loyalty = LoyaltyPoints.objects.get(
                        Q(loyaltytype='Service') |
                        Q(loyaltytype='Both'),
                        location=location,
                        # amount_spend = total_price,
                        is_active=True,
                        is_deleted=False
                    )
                client_points, created = ClientLoyaltyPoint.objects.get_or_create(
                    location=location,
                    client=client,
                    loyalty_points=location_loyalty, # loyalty Foreignkey
                    )
                amount_for_calcluating_point = (sub_total/location_loyalty.amount_spend) * location_loyalty.number_points
                earned_points = amount_for_calcluating_point * location_loyalty.number_points
                wallet_reward_amount = location_loyalty.total_earn_from_points * (location_loyalty.earn_points * earned_points)
                if created:
                    client_points.total_earn = earned_points
                    client_points.total_amount = wallet_reward_amount
                else:
                    client_points.total_earn = float(client_points.total_earn) + float(earned_points)
                    client_points.total_amount = client_points.total_amount + float(wallet_reward_amount)
                client_points.for_every_points = location_loyalty.earn_points
                client_points.customer_will_get_amount = location_loyalty.total_earn_from_points

                client_points.save()

                LoyaltyPointLogs.objects.create(
                    location=location,
                    client=client_points.client,
                    client_points=client_points,
                    loyalty=location_loyalty,
                    points_earned=earned_points,
                    points_redeemed=logs_points_redeemed,
                    balance=client_points.total_available_points,
                    actual_sale_value_redeemed=logs_total_redeened_value,
                    invoice=invoice,
                    checkout=sale_record,
                )
                
            else:
                pass
        except Exception as e:
                return f"error coming through loyalty_points {str(e)}"