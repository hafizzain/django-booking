

from rest_framework import serializers

from .models import Deal, DealRestriction, DealMedia, DealDay, DealDate
class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = '__all__'
        optional_fields = ['usagePerCustomer', 'validPeriod']


class DealRestrictionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DealRestriction
        fields = [
            'id',
            'deal',
            'excluded_products',
            'excluded_services',
            'block_dates',
            'excluded_locations',
        ]
        optional_fields = [
            'excluded_products',
            'excluded_services',
            'block_dates',
            'excluded_locations',
        ]