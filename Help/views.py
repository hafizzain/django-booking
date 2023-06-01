from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import HelpContent
from rest_framework import status
from .serializers import *
import json


@api_view(['POST'])
@permission_classes([AllowAny])
def add_query(request):
    content = request.data.get('content')
    parent_comment = request.data.get('parent_comment', None)
    print(parent_comment)

    if content is None:
        return Response(
            {
                'success':False,
                'status_code':400,
                'status_code_text' : '400',
                'response':
                {
                    'message':'Invalid data',
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    comment_obj = HelpContent.objects.create(content=content)

    if parent_comment is not None:

        try:
            parent = HelpContent.objects.get(id = parent_comment)
            print(parent)
        except Exception as e:
            return Response(
                {
                    'success':False,
                    'message':'Data Not Found, Invalid Parent ID',
                    'status_code':400,
                    'status_code_text' : '400',
                    'response':
                    {
                        'message':str(e),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        parent.is_parent = True
        parent.save()
        comment_obj.parent_comment = parent
        comment_obj.save()
    else:
        comment_obj.is_parent = True
        comment_obj.save()


    return Response(
        {
            'success':True,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'Created Successfully',
                'response':str(comment_obj),
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_comment(request):
    try:
        all_comments = HelpContent.objects.filter(is_parent = True, parent_comment__isnull = True)
    except Exception as e:
        return Response(
            {
                'success':False,
                'message':'Data Not Found',
                'status_code':400,
                'status_code_text' : '400',
                'response':
                {
                    'message':str(e),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    comments = HelpContentSerializer(all_comments, many=True)

    return Response(
    {
        'success':True,
        'status_code':200,
        'status_code_text' : '200',
        'response':
        {
            'message':'Data Returned Successfully',
            'response':comments.data,
            'error_message': None
        }
    },
    status=status.HTTP_200_OK
)




@api_view(['GET'])
@permission_classes([AllowAny])
def get_comment_details(request):
    id = request.GET.get('id')

    try:
        all = HelpContent.objects.filter(parent_comment=id).order_by('content')
    except Exception as e:
        return Response(
            {
                'success':False,
                'message':'Data Not Found, Invalid ID',
                'status_code':400,
                'status_code_text' : '400',
                'response':
                {
                    'message':str(e),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    
    leng = len(all)
    serializer = HelpContentSerializer(all, many=True)
    print(serializer)
    if leng == 0:
        message = 'No Child Data'
    else:
        message = 'Returned Successfully'
    
    return Response(
        {
            'success':True,
            'length':leng,
            'message':message,
            'response':{
                'data':serializer.data
            }
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_comment(request):
    id = request.data.get('id')

    try:
        comment = HelpContent.objects.get(id=id)
    except Exception as e:
        return Response(
            {
                'success':False,
                'message':'Not Found',
                'status_code':400,
                'status_code_text' : '400',
                'response':
                {
                    'message':str(e),
                }
            },
        status=status.HTTP_404_NOT_FOUND
        )

    comment.delete()

    return Response(
        {
            'success':True,
            'message':'Deleted Successfully',
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def update_comment(request):
    id = request.data.get('id')
    content = request.data.get('content')

    if content is None:
        return Response(
            {
                'success':False,
                'status_code':400,
                'status_code_text' : '400',
                'response':
                {
                    'message':'Invalid data',
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    try:
        comment = HelpContent.objects.get(id=id)
    except Exception as e:
        return Response(
            {
                'success':False,
                'message':'Not Found',
                'status_code':400,
                'status_code_text' : '400',
                'response':
                {
                    'message':str(e),
                }
            },
        status=status.HTTP_404_NOT_FOUND
        )

    comment.content = content
    comment.save()

    return Response(
        {
            'success':True,
            'message':'Updated Successfully',
        },
        status=status.HTTP_200_OK
    )

