

from rest_framework import serializers

from .models import Deal, DealRestriction, DealMedia, DealDay, DealDate
class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = '__all__'
        optional_fields = ['usagePerCustomer', 'validPeriod']


class GetAllDealsSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')
    class Meta:
        model = Deal
        fields = [
            'id',
            'title',
            'deal_type',
            'category',
            'customerType',
            'status',
        ]


class BlockDateSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    def get_date(self, obj):
        return obj.date.strftime("%Y-%m-%d")

    class Meta:
        model = DealDate
        fields = ['date']


class DealRestrictionSerializer(serializers.ModelSerializer):
    block_dates = serializers.SerializerMethodField(read_only=True)

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
    
        # Assuming block_dates is a ManyToManyField related to a BlockDate model
        
    
    def to_representation(self, instace):
        data = super(DealRestrictionSerializer, self).to_representation(instace)
        data['block_dates'] = [date.date.strftime("%Y-%m-%d") for date in obj.block_dates.all()]
        return data