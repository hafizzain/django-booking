


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from Business.models import BusinessType
from Business.serializers.v1_serializers import BusinessTypeSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_types(request):
    all_types = BusinessType.objects.filter(
        is_active=True,
        is_deleted=False
    )
    serialized = BusinessTypeSerializer(all_types, many=True)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All business types',
                'data' : serialized.data
            }
        }
    )