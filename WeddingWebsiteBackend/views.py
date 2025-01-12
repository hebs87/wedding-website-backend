from django.shortcuts import render


def home(request):
    """ Render the index.html template to enable healthcheck URL returning 200 when landing on root URL """
    return render(request, 'index.html')
