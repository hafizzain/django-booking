

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
    block_dates = serializers.DateTimeField(read_only=True, source='block_dates.date', format="%Y-%m-%d")

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
    
    # def to_representation(self, instace):
    #     data = super(DealRestrictionSerializer, self).to_representation(instace)
    #     data['block_dates'] = 
    #     permissions = self.get_permissions(instace)
    #     # return permissions.update({
    #     #     'id': instace.id,
    #     #     'name': instace.full_name,

    #     # })
    #     return {
    #         "nme": instace.full_name,
    #         permissions: permissions
    #     }