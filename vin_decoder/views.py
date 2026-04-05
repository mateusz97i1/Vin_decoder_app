import requests,json

from .forms import InputVinForm
from django.shortcuts import render , redirect
from requests import request
from openai import OpenAI
from .services import get_vehicle_data_vin
# Create your views here.



def home(request):

    car_info = None
    message_error = None
    vin = None
    form_vin =InputVinForm(request.GET or None)

    if request.method == "GET" and form_vin.is_valid():

        vin = form_vin.cleaned_data['vin_number']
        car_info, message_error = get_vehicle_data_vin(vin)

    return render(request, 'home.html',{
        'car_info': car_info,
        'message_error': message_error,
        'vin': vin,
        'form_vin':form_vin
        })


def openai_get_car_info():

    pass