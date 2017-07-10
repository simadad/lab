from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
# Create your views here.


def register(request):
    return HttpResponse('<h1>register</h1>')


def log_in(request):
    if request.methord == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            user = User.objects.get(username=username)
            login(request, user)
            return HttpResponse(render(request, 'account/logout.html'))
        else:
            return HttpResponse()
    else:
        next_url = request.GET.get('next')



def log_out(request):
    pass
