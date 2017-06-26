from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def register(request):
    return HttpResponse('<h1>register</h1>')


def log_in(request):
    return HttpResponse('<h1>login</h1>')
