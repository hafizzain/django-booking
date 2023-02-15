

from Employee.models import Employee
from Employee.serializers import EmployeSerializer
from rest_framework import serializers
from Authentication.models import AccountType, User
from Tenants.models import ClientIdUser, Domain, Tenant

class UserSerializer(serializers.ModelSerializer):
    # access_token = serializers.SerializerMethodField()

    def get_access_token(self,obj):
        return str(obj.auth_token)

    class Meta:
        model = User
        fields = '__all__'

class UserLoginSerializer(serializers.ModelSerializer):
    access_token = serializers.SerializerMethodField()
    domain = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    employee_permission = serializers.SerializerMethodField()
    
    def get_employee(self, obj):
        try:
            employee = self.context["employee"]
            if employee:
                return True
            else:
                return False
        except Exception as err:
            return str(err)
        
    def get_employee_permission(self, obj):
        try:
            
            emp = Employee.objects.get(email = obj.email)
            return EmployeSerializer(emp, context=self.context).data#context={'request' : request, })
            
        except Exception as err:
            return str(err)
    
    def get_access_token(self,obj):
        return str(obj.auth_token)

    def get_domain(self,obj):
        try:
            user_domain = Domain.objects.get(
                user=obj,
                is_deleted=False,
                is_blocked=False,
                is_active=True
            )
            return user_domain.schema_name
        except Exception as err:
            return None

    class Meta:
        model = User
        fields = [
            'id',
            'domain',
            'access_token',  'employee', 'employee_permission',
        ]

class UserTenantSerializer(serializers.ModelSerializer):
    domain = serializers.SerializerMethodField()
    is_tenant = serializers.SerializerMethodField()
    # access_token = serializers.SerializerMethodField()

    # def get_access_token(self,obj):
    #     return str(obj.auth_token)


    def get_is_tenant(self,obj):
        try:
            obj.tenant
            return True
        except Exception as err:
            return False

    def get_domain(self,obj):
        try:
            user_domain = Domain.objects.get(
                user=obj,
                is_deleted=False,
                is_blocked=False,
                is_active=True
            )
            return user_domain.schema_name
        except Exception as err:
            return None

    class Meta:
        model = User
        fields = [
            # 'id',
            'domain',
            'is_tenant',
            # 'access_token'
        ]
    

class UserTenantLoginSerializer(serializers.ModelSerializer):
    domain = serializers.SerializerMethodField()
    is_tenant = serializers.SerializerMethodField()
    access_token = serializers.SerializerMethodField()
    
    def get_access_token(self,obj):
        return str(obj.auth_token)


    def get_is_tenant(self,obj):
        try:
            obj.tenant
            return True
        except Exception as err:
            return False

    def get_domain(self,obj):
        try:
            user_domain = Domain.objects.get(
                user=obj,
                is_deleted=False,
                is_blocked=False,
                is_active=True
            )
            return user_domain.schema_name
        except Exception as err:
            return None
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email',
                  'domain', 'is_tenant', 'access_token','joined_at', ]
        
class UserSerializerByClient(serializers.ModelSerializer):
    domain = serializers.SerializerMethodField()
    is_tenant = serializers.SerializerMethodField()
    access_token = serializers.SerializerMethodField()
    account_type = serializers.SerializerMethodField()
    client_id = serializers.SerializerMethodField()
    
    def get_client_id(self,obj):
        try:
            id = ClientIdUser.objects.get(user = obj)
            return id.client_id
        except Exception as err:
            return str(err)
            pass
    

    def get_account_type(self,obj):
        try:
            account_type = AccountType.objects.get(user = obj)
            return account_type.account_type
        except Exception as err:
            pass
        
    def get_access_token(self,obj):
        return str(obj.auth_token)


    def get_is_tenant(self,obj):
        try:
            obj.tenant
            return True
        except Exception as err:
            return False

    def get_domain(self,obj):
        try:
            user_domain = Domain.objects.get(
                user=obj,
                is_deleted=False,
                is_blocked=False,
                is_active=True
            )
            return user_domain.schema_name
        except Exception as err:
            return None
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 
                  'domain', 'is_tenant', 'access_token','joined_at', 'account_type', 'client_id']
        
