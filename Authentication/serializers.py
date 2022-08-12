

from rest_framework import serializers
from Authentication.models import User
from Tenants.models import Domain, Tenant

class UserSerializer(serializers.ModelSerializer):
    # access_token = serializers.SerializerMethodField()

    def get_access_token(self,obj):
        return str(obj.auth_token)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'mobile_number',
            'joined_at',
            'is_superuser',
            'is_admin',
            'is_staff',
            'is_active',
            # 'access_token'
        ]

class UserLoginSerializer(serializers.ModelSerializer):
    access_token = serializers.SerializerMethodField()
    domain = serializers.SerializerMethodField()

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
            'access_token'
        ]

class UserTenantSerializer(serializers.ModelSerializer):
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
        fields = [
            'id',
            'domain',
            'is_tenant',
            'access_token'
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
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'domain', 'is_tenant', 'access_token']