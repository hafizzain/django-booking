from rest_framework import serializers
from .models import EmployeeBookingDailyInsights


class EmployeeDailyInsightsSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeBookingDailyInsights
        fields = '__all__'
