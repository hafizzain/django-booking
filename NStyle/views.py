from django.shortcuts import render


def email_template_view(request):
    file = request.GET.get('file')
    context = {
        
    }
    return render(request, file, context)