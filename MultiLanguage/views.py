from django.shortcuts import render, HttpResponse, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import *
from rest_framework import status
from .serializers import *
import json
from .models import Language as Lang
from django.db import transaction




def add_language(request):
    lang = request.POST.get('lang', None)
    icon = request.POST.get('icon', None)

    language = Lang(title=lang, icon=icon)
    language.save()

    new_language = Lang.objects.get(title__icontains = lang)

    first_language = Lang.objects.get(title__icontains = 'arabic')
    
    labels = TranslationLabels.objects.filter(language = first_language)
    if len(labels) == 0:
        pass
    else:
        for label in labels:
            label_instance = TranslationLabels(english_name=label.english_name, value=label.english_name, key=label.english_name, order=label.order )
            
            language = Lang.objects.get(id = new_language.id)
            label_instance.language = language
            
            label_instance.save()

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
    if request.method == "POST":
        english_name = request.POST.get('english_name')
        value = request.POST.get('value')
        last_instance = Labels.objects.all()[0]
        order = int(last_instance.order) +1
        lang = request.POST.get('lang')


    label = TranslationLabels(english_name=english_name, value=value, key=english_name, order=order )

    lang = Language.objects.get(id = lang.id)
    label.language = lang

    label.save()


    detail= f'/super-admin/language'
    return redirect(detail)



def get_data(request):
    language = request.GET.get('language', None)
    
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

    try:
        trans = TranslationLabels.objects.filter(language__title=language)
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
    return render(request, 'SuperAdminPanel/pages/language/language-section-detail.html', {'trans':trans, 'language':language})



def edit_translation_forms(request):
    if request.method == 'POST':
        language = request.POST.get('language', None)
        id = request.POST.get('id')
        translation = request.POST.get('value')
        english_name = request.POST.get('english_name')
        trans = TranslationLabels.objects.get(id = id)
        trans.value = translation
        trans.english_name = english_name
        trans.save()
        return redirect(f'/api/v1/multilanguage/get_data/?language={language}')
    return redirect(f'/api/v1/multilanguage/get_data/?language={language}')

def add_translation_forms(request):
    if request.method == 'POST':
        language = request.POST.get('language', None)
        english_name = request.POST.get('english_name')
        value = request.POST.get('value')
        try:
            last_instance = TranslationLabels.objects.all()[0]
            order = int(last_instance.order) +1

        except:
            last_instance = 0
            order = last_instance + 1


        label = TranslationLabels(english_name=english_name, value=value, key=english_name, order=order )
        lang = Lang.objects.get(title = language)
        label.language = lang
        label.save()
        
        return redirect(f'/api/v1/multilanguage/get_data/?language={language}')
    return redirect(f'/api/v1/multilanguage/get_data/?language={language}')



@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_invoiceTranslation(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        invoice = request.POST.get('invoice')
        items = request.POST.get('items')
        amount = request.POST.get('amount')
        subtotal = request.POST.get('subtotal')
        tips = request.POST.get('tips')
        taxes = request.POST.get('taxes')
        total = request.POST.get('total')
        change =  request.POST.get('change')
        payment_method = request.POST.get('payment_method')
        statuss = request.POST.get('status')

        invoiceTranslation = InvoiceTranslation(
            invoice = invoice,
            items = items,
            amount = amount,
            subtotal = subtotal,
            tips = tips,
            taxes = taxes,
            total = total,
            payment_method = payment_method,
            change = change,
            status = statuss
        )
        invoiceTranslation.user = request.user
        invoiceTranslation.save()


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
@permission_classes([IsAuthenticated])
def get_invoiceTranslation(request):
    allInvoicTrans = InvoiceTranslation.objects.all()
    
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
                    'status_code':200,
                    'status_code_text' : '200',
                    'response':
                    {
                        'message':'No Data Found',
                        'data':[]
                    }
                },
                status=status.HTTP_200_OK
            )

@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_invoiceTranslation(request):
    id = request.POST.get('id', None)
    language = request.POST.get('language')
    invoice = request.POST.get('invoice')
    items = request.POST.get('items')
    amount = request.POST.get('amount')
    subtotal = request.POST.get('subtotal')
    tips = request.POST.get('tips')
    taxes = request.POST.get('taxes')
    total = request.POST.get('total')
    change =  request.POST.get('change')
    payment_method = request.POST.get('payment_method')
    statuss = request.POST.get('status')

    user = request.user

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
        invoice_data.change = change
        invoice_data.payment_method = payment_method
        invoice_data.status = statuss

        language = AllLanguages.objects.get(id__icontains = str(language))        
        invoice_data.language = language

        invoice_data.user = user


        invoice_data.save()
        invoiceTranslation_data = InvoiceTransSerializer(invoice_data).data

        return Response(
                {
                    'success':True,
                    'status_code':200,
                    'status_code_text' : '200',
                    'response':
                    {
                        'message':'Invoice Translation Updated Successfully',
                        'data': invoiceTranslation_data
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
@permission_classes([IsAuthenticated])
def delete_invoiceTranslation(request):
    id = request.GET.get('id', None)
    user = request.user    

    if id:
        try:
            invoice = InvoiceTranslation.objects.get(id = id)
        except Exception as e:
            return Response(
                {
                    'success':True,
                    'status_code':200,
                    'status_code_text' : '200',
                    'response':
                    {
                        'message':'Invalid ID',
                    }
                },
                status=status.HTTP_200_OK
            )
    
 
        if invoice.user == user:
            invoice.delete()
        else:
            return Response(
                {
                    'success':True,
                    'status_code':200,
                    'status_code_text' : '200',
                    'response':
                    {
                        'message':'You are not allowed to delete it',
                        'data':[]
                    }
                },
                status=status.HTTP_200_OK
            )
    
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
    





@api_view(['GET'])
@permission_classes([AllowAny])
def get_LanguageTranslation(request):
    language = request.GET.get('language')

    if language is None:
        return Response(
        {
            'success':False,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'InValid Language',
                'data':[]
            }
        },
        status=status.HTTP_200_OK
    )


    labels = TranslationLabels.objects.filter(language__title__icontains = language).order_by('order')

    serializer = TranslationLabelsSerializer(labels,many=True).data

    if len(labels) == 0:
        return Response(
        {
            'success':False,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'No Data Found',
                'data':[]
            }
        },
        status=status.HTTP_200_OK
    )    

    return Response(
        {
            'success':True,
            'status_code':200,
            'status_code_text' : '200',
            'response':
            {
                'message':'Data Found',
                'data':serializer
            }
        },
        status=status.HTTP_200_OK
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
