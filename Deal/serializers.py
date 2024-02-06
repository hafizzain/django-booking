

from rest_framework import serializers

from .models import Deal, DealRestriction, DealMedia, DealDay, DealDate
class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = '__all__'


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