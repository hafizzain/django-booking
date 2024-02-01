
from datetime import datetime, timedelta


def calculate_validity(validity):
    current_date = datetime.now()

    parts = validity.split()
    num = int(parts[0])
    unit = parts[1].lower()

    unit_factors = {
        'day': 1,
        'days': 1,
        'month': 30,  # Assuming 30 days per month for simplicity
        'months': 30,
        'year': 365,  # Assuming 365 days per year for simplicity
        'years': 365
    }

    # Calculate expiry date
    expiry_date = current_date + timedelta(days=num * unit_factors.get(unit, 0))

    # Format the expiry date as a string
    formatted_expiry = expiry_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    return formatted_expiry