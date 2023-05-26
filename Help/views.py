from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Comment
from rest_framework import status
from .serializers import *
import json


@api_view(['POST'])
@permission_classes([AllowAny])
def add_query(request):
    content = request.data.get('content')
    parent_comment = request.data.get('parent_comment', None)
    is_parent = request.data.get('is_parent', None)

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
    
    # comment = CommentSerializer(data = request.data)
    # if comment.is_valid():
    #     comment.save()

    try:
        comment_obj = Comment.objects.create(content=content)
        if parent_comment is not None:
            parent = Comment.objects.get(id = parent_comment)
            parent.is_parent = True
            parent.save()
            comment_obj.parent_comment = parent
    except Exception as e:
        return Response(
            {
                'success':False,
                'status_code':400,
                'status_code_text' : '400',
                'response':
                {
                    'message':str(e),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        pass

    comment_obj.save()

    return Response(
        {
            'success':True,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'Created Successfully',
                'response':json.loads(str(comment_obj)),
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_comment(request):
    id = request.GET.get('id', None)
    if id is not None:
        pass
    else:
        all_comments = Comment.objects.filter(is_parent = True)

        comments = CommentSerializer(all_comments, many=True)

        return Response(
        {
            'success':True,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'Returned Successfully',
                'response':comments.data,
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )

    