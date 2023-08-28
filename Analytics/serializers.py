from rest_framework import serializers
from .models import EmployeeBookingDailyInsights


class EmployeeDailyInsightsSerializer(serializers.ModelSerializer):

    time_debug = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeBookingDailyInsights
        fields = ['created_at', 'time_debug', 'day_time_choices']


    def get_time_debug(self, obj):
        return obj.created_at.time().replace(tzinfo=None)