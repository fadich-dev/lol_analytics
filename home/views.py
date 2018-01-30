from django.shortcuts import render

# Create your views here.


def home(request):
    name = ''
    region = ''
    params = request.GET
    if 'acc' in params:
        name = request.GET['acc']
    if 'reg' in params:
        region = request.GET['reg']

    return render(request, 'homepage.html', {
        'name': name,
        'region': region
    })
