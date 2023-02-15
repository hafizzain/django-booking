from dataclasses import fields
from datetime import datetime
from genericpath import exists
from pyexpat import model
from Appointment.models import AppointmentCheckout
from Business.models import BusinessAddress
from Employee.models import Employee
from TragetControl.models import StaffTarget
from Product.Constants.index import tenant_media_base_url, tenant_media_domain


from rest_framework import serializers

from Authentication.models import AccountType, User

class EmployeeDashboradSerializer(serializers.ModelSerializer):
    achieve_target = serializers.SerializerMethodField(read_only=True)
    
    def get_achieve_target(self, obj):
        try:
            range_start = self.context["range_start"]
            range_end = self.context["range_end"]
            if range_start:
                range_start = datetime.strptime(range_start, "%Y-%m-%d")
                range_end = datetime.strptime(range_end, "%Y-%m-%d")
            else:
                range_end = datetime.now()
                month = range_end.month
                year = range_end.year
                range_start = f'{year}-{month}-01'
                range_start = datetime.strptime(range_start, "%Y-%m-%d")
                
            targets =  StaffTarget.objects.get(
                employee = obj.id,
                year__gte =  range_start ,
                year__lte =  range_start ,
                )
            total_targets = int(targets.service_target) + int(targets.retail_target)
        except Exception as err:
            return str(err)
    
    class Meta:
        model = Employee
        fields=['id', 'full_name','achieve_target',  ]


# class TargetsAcheivedSerializer(serializers.ModelSerializer):
#     achieve_target = serializers.SerializerMethodField(read_only=True)
    
#     def get_achieve_target(self, obj):
        
#         range_start = self.context.GET.get("range_start", None)
#         range_end = self.context.GET.get("range_end", None)

#         if range_start is not None:
#             range_start = datetime.strptime(range_start, "%Y-%m-%d")
#             range_end = datetime.strptime(range_end, "%Y-%m-%d")
#         else:
#             range_end = datetime.now()
#             month = range_end.month
#             year = range_end.year
#             range_start = f'{year}-{month}-01'
#             range_start = datetime.strptime(range_start, "%Y-%m-%d")
#         try:
#             targets =  StaffTarget.objects.get(
#                 employee = obj.id,
#                 year__gte =  range_start ,
#                 year__lte =  range_end ,
#                 )
#             acheived_targets = int(targets.achieve_target) + int(targets.service_target) + int(targets.retail_target)
#         except Exception as err:
#             return str(err)
#         return None
    
#     class Meta:
#         model = Employee
#         fields=['id','range_start','range_end',]

class GraphDataSerializer(serializers.ModelSerializer):
    
    GraphData = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = StaffTarget
        fields = ('service_target','retail_target','voucher_target', 'membership_target','total_set')