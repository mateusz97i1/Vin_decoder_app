from django.shortcuts import render , redirect
from requests import request
# Create your views here.


def home(request):

    return render(request,'home.html')