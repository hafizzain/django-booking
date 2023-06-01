from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import *
from rest_framework import status
from .serializers import *
import json




@api_view(['POST'])
@permission_classes([AllowAny])
def add_data(request):
    language = request.data.get('language', None)
    section = request.data.get('section', None)
    data = request.data.get('data')

    if language is None:
        return Response(
        {
            'success':False,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'Language Cannot be empty',
            }
        },
        status=status.HTTP_200_OK
    )

    if section is None:
        return Response(
        {
            'success':False,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'Section Cannot be empty',
            }
        },
        status=status.HTTP_200_OK
    )

    if data is None:
        return Response(
        {
            'success':False,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'Data Cannot be empty',
            }
        },
        status=status.HTTP_200_OK
    )

    try:
        lan = Language.objects.get(title = language)
    except:
        lang = Language.objects.create(title = language)
        lang.save()

    for data in data:
        label = data.get('label')
        value = data.get('value')

        try:
            labels = Labels.objects.get(label = label, section=section, language__title = language)
            labels.value = value
            labels.save()
        except:
            labels = Labels.objects.create(label = label, value=value, section=section)

            try:
                lan = Language.objects.get(title=language)
            except Exception as e:
                return Response(
                    {
                        'success':False,
                        'status_code':200,
                        'status_code_text' : '200',
                        'response':
                        {
                            'message':'Invalid Language Input',
                        }
                    },
                    status=status.HTTP_200_OK
                )
            
            labels.language = lan
            labels.save()

    return Response(
        {
            'success':True,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'Label Created Successfully',
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_data(request):
    language = request.GET.get('language', None)
    section = request.GET.get('section', None)
    
    if language is None:
        return Response(
        {
            'success':False,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'Language Cannot be empty',
            }
        },
        status=status.HTTP_200_OK
    )

    if section is None:
        return Response(
        {
            'success':False,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'Section Cannot be empty',
            }
        },
        status=status.HTTP_200_OK
    )


    try:
        data = Labels.objects.filter(language__title=language, section = section)
    except Exception as e:
            return Response(
                {
                    'success':False,
                    'status_code':200,
                    'status_code_text' : '200',
                    'response':
                    {
                        'message':'No Data Found',
                    }
                },
                status=status.HTTP_200_OK
            )

    serializer = LabelSerializer(data, many=True)

    return Response(
        {
            'success':True,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'Returned Successfully',
                'data':serializer.data,
            }
        },
        status=status.HTTP_200_OK
    )
