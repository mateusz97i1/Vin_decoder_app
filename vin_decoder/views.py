import requests,json

from django.shortcuts import render , redirect
from requests import request
from openai import OpenAI
from .services import get_vehicle_data_vin
# Create your views here.



def home(request):
    vin = request.GET.get("vin", "").strip()
    
    car_info = None
    message_error = None

    if vin:
        car_info, message_error = get_vehicle_data_vin(vin)

    return render(request, 'home.html',
                   {'car_info': car_info,
                    'message_error': message_error,
                    'vin': vin})


def openai_get_car_info():

    pass