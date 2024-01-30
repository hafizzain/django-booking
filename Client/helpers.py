
from datetime import datetime, timedelta


def calculate_validity(validaty):
    current_date = datetime.now()

    # Parse duration string
    parts = validaty.split()
    num = int(parts[0])
    unit = parts[1].lower()

    # Define conversion factors
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

    return expiry_date