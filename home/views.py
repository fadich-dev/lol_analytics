from django.shortcuts import render

# Create your views here.


def home(request):
    name = request.GET.get('account', '')
    region = request.GET.get('region', '')

    return render(request, 'homepage.html', {
        'name': name,
        'region': region
    })
