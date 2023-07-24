from django.shortcuts import render, HttpResponse, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import *
from rest_framework import status
from .serializers import *
import json




def add_language(request):
    language = request.POST.get('language')
    icon = request.POST.get('icon')

    lang = Language.objects.create(title=language, icon=icon)
    lang.save()

    return redirect('/super-admin/language/')


def add_section(request):
    lang = request.GET.get('language')
    title = request.POST.get('title')
    icon = request.POST.get('icon')
    print(lang, title)

    section = Section.objects.create(title=title, icon=icon)
    language = Language.objects.get(title = lang)
    section.language = language
    section.save()

    detail= f'/super-admin/language/section/?language={lang}'
    return redirect(detail)



def add_labels(request):

    lang = request.POST.get('lang')
    section = request.POST.get('section')
    label = request.POST.get('label')
    value = request.POST.get('value')
    print(lang, section, label, value)
    try:
        section = Section.objects.get(language__title=lang, title=section)
    except:
        pass

    try:
        old_label = Labels.objects.get(label=label, section__title=section, section__language__title = lang)
        old_label.value= value
        old_label.save()
    except:        
        labels = Labels.objects.create(label=label, value=value)
        labels.section = section
        labels.save()


    detail= f'/super-admin/language/section-detail/?language={lang}&section={ section }'
    return redirect(detail)



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
        data = Labels.objects.filter(section__language__title=language, section__title = section)
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


@api_view(['POST'])
@permission_classes([AllowAny])
def add_invoiceTranslation(request):
    if request.method == 'POST':
        location = request.POST.get('location')
        language = request.POST.get('language')
        invoice = request.POST.get('invoice')
        items = request.POST.get('items')
        amount = request.POST.get('amount')
        subtotal = request.POST.get('subtotal')
        tips = request.POST.get('tips')
        taxes = request.POST.get('taxes')
        total = request.POST.get('total')
        payment_method = request.POST.get('payment_method')
        statuss = request.POST.get('status')


        loc = location

        invoiceTranslation = InvoiceTranslation(
            invoice = invoice,
            items = items,
            amount = amount,
            subtotal = subtotal,
            tips = tips,
            taxes = taxes,
            total = total,
            payment_method = payment_method,
            status = statuss
        )
        try:
            location = BusinessAddress.objects.get(id__icontains = str(location))
            invoiceTranslation.location = location
        except Exception as e:
            return Response(
            {
                'success':False,
                'status_code':204,
                'status_code_text' : '204',
                'response':
                {
                    'message':'Location Not Founf',
                    'data': str(e),
                    'location':loc,
                    'tips':tips
                }
            },
            status=status.HTTP_201_CREATED
            )


        language = AllLanguages.objects.get(id__icontains = str(language))        
        invoiceTranslation.language = language

        invoiceTranslation.save()

        invoiceTranslation_data = InvoiceTransSerializer(invoiceTranslation).data

        return Response(
            {
                'success':True,
                'status_code':200,
                'status_code_text' : 'success',
                'response':
                {
                    'message':'Invoice Translation Added Successfully',
                    'data': invoiceTranslation_data
                }
            },
            status=status.HTTP_200_OK
        )

    return Response(
            {
                'success':True,
                'status_code':204,
                'status_code_text' : '204',
                'response':
                {
                    'message':'Invalid Input',
                }
            },
            status=status.HTTP_204_NO_CONTENT
        )
    

@api_view(['GET'])
@permission_classes([AllowAny])
def get_invoiceTranslation(request):
    allInvoicTrans = InvoiceTranslation.objects.filter(status='active')
    
    if allInvoicTrans:
        translation_data = InvoiceTransSerializer(allInvoicTrans, many=True).data

        return Response(
                {
                    'success':True,
                    'status_code':200,
                    'status_code_text' : '200',
                    'response':
                    {
                        'message':'Data REturend Successfully',
                        'data':translation_data
                    }
                },
                status=status.HTTP_200_OK
            )
    
    else:
        return Response(
                {
                    'success':True,
                    'status_code':204,
                    'status_code_text' : '204',
                    'response':
                    {
                        'message':'No Data Found',
                        'data':[]
                    }
                },
                status=status.HTTP_204_NO_CONTENT
            )

@api_view(['POST'])
@permission_classes([AllowAny])
def update_invoiceTranslation(request):
    id = request.POST.get('id', None)
    location = request.POST.get('location')
    language = request.POST.get('language')
    invoice = request.POST.get('invoice')
    items = request.POST.get('items')
    amount = request.POST.get('amount')
    subtotal = request.POST.get('subtotal')
    tips = request.POST.get('tips')
    taxes = request.POST.get('taxes')
    total = request.POST.get('total')
    payment_method = request.POST.get('payment_method')
    statuss = request.POST.get('status')


    if id:
        try:
            invoice_data = InvoiceTranslation.objects.get(id = id)
        except:
            return Response(
                {
                    'success':False,
                    'status_code':204,
                    'status_code_text' : '204',
                    'response':
                    {
                        'message':'Invalid Id',
                        'data':[]
                    }
                },
                status=status.HTTP_204_NO_CONTENT
            )

        invoice_data.invoice = invoice
        invoice_data.items = items
        invoice_data.amount = amount
        invoice_data.subtotal = subtotal
        invoice_data.tips = tips
        invoice_data.taxes = taxes
        invoice_data.total = total
        invoice_data.payment_method = payment_method
        invoice_data.status = statuss

        location = BusinessAddress.objects.get(id__icontains = str(location))
        invoice_data.location = location

        language = AllLanguages.objects.get(id__icontains = str(language))        
        invoice_data.language = language

        invoice_data.save()

        return Response(
                {
                    'success':True,
                    'status_code':200,
                    'status_code_text' : '200',
                    'response':
                    {
                        'message':'Invoice Translation Updated Successfully',
                        'data':[]
                    }
                },
                status=status.HTTP_200_OK
            )
    
    else:
        return Response(
                {
                    'success':False,
                    'status_code':204,
                    'status_code_text' : '204',
                    'response':
                    {
                        'message':'Id cannot be empty',
                        'data':[]
                    }
                },
                status=status.HTTP_204_NO_CONTENT
            )
    


@api_view(['GET'])
@permission_classes([AllowAny])
def delete_invoiceTranslation(request):
    id = request.GET.get('id', None)

    if id:
        invoice = InvoiceTranslation.objects.get(id = id)
        invoice.delete()
        return Response(
                {
                    'success':True,
                    'status_code':200,
                    'status_code_text' : '200',
                    'response':
                    {
                        'message':'Data Deleted Successfully',
                        'data':[]
                    }
                },
                status=status.HTTP_200_OK
            )
    
    else:
        return Response(
                {
                    'success':False,
                    'status_code':204,
                    'status_code_text' : '204',
                    'response':
                    {
                        'message':'No Data Found',
                        'data':[]
                    }
                },
                status=status.HTTP_204_NO_CONTENT
            )
    


    























# @api_view(['POST'])
# @permission_classes([AllowAny])
# def add_data(request):
#     language = request.data.get('language', None)
#     section = request.data.get('section', None)
#     data = request.data.get('data')

#     if language is None:
#         return Response(
#         {
#             'success':False,
#             'status_code':200,
#             'status_code_text' : '200',
#             'response':
#             {
#                 'message':'Language Cannot be empty',
#             }
#         },
#         status=status.HTTP_200_OK
#     )

#     if section is None:
#         return Response(
#         {
#             'success':False,
#             'status_code':200,
#             'status_code_text' : '200',
#             'response':
#             {
#                 'message':'Section Cannot be empty',
#             }
#         },
#         status=status.HTTP_200_OK
#     )

#     if data is None:
#         return Response(
#         {
#             'success':False,
#             'status_code':200,
#             'status_code_text' : '200',
#             'response':
#             {
#                 'message':'Data Cannot be empty',
#             }
#         },
#         status=status.HTTP_200_OK
#     )

#     try:
#         lan = Language.objects.get(title = language)
#     except:
#         lang = Language.objects.create(title = language)
#         lang.save()

#     for data in data:
#         label = data.get('label')
#         value = data.get('value')

#         try:
#             labels = Labels.objects.get(label = label, section=section, language__title = language)
#             labels.value = value
#             labels.save()
#         except:
#             labels = Labels.objects.create(label = label, value=value, section=section)

#             try:
#                 lan = Language.objects.get(title=language)
#             except Exception as e:
#                 return Response(
#                     {
#                         'success':False,
#                         'status_code':200,
#                         'status_code_text' : '200',
#                         'response':
#                         {
#                             'message':'Invalid Language Input',
#                         }
#                     },
#                     status=status.HTTP_200_OK
#                 )
            
#             labels.language = lan
#             labels.save()

#     return Response(
#         {
#             'success':True,
#             'status_code':200,
#             'status_code_text' : '200',
#             'response':
#             {
#                 'message':'Label Created Successfully',
#             }
#         },
#         status=status.HTTP_200_OK
#     )


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_data(request):
#     language = request.GET.get('language', None)
#     section = request.GET.get('section', None)
    
#     if language is None:
#         return Response(
#         {
#             'success':False,
#             'status_code':200,
#             'status_code_text' : '200',
#             'response':
#             {
#                 'message':'Language Cannot be empty',
#             }
#         },
#         status=status.HTTP_200_OK
#     )

#     if section is None:
#         return Response(
#         {
#             'success':False,
#             'status_code':200,
#             'status_code_text' : '200',
#             'response':
#             {
#                 'message':'Section Cannot be empty',
#             }
#         },
#         status=status.HTTP_200_OK
#     )


#     try:
#         data = Labels.objects.filter(language__title=language, section = section)
#     except Exception as e:
#             return Response(
#                 {
#                     'success':False,
#                     'status_code':200,
#                     'status_code_text' : '200',
#                     'response':
#                     {
#                         'message':'No Data Found',
#                     }
#                 },
#                 status=status.HTTP_200_OK
#             )

#     serializer = LabelSerializer(data, many=True)

#     return Response(
#         {
#             'success':True,
#             'status_code':200,
#             'status_code_text' : '200',
#             'response':
#             {
#                 'message':'Returned Successfully',
#                 'data':serializer.data,
#             }
#         },
#         status=status.HTTP_200_OK
#     )
