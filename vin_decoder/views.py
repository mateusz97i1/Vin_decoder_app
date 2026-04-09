import requests,json

from .forms import InputVinForm
from django.shortcuts import render , redirect
from requests import request
from openai import OpenAI
from .services import get_vehicle_data_vin
# Create your views here.

#focus rs vin number
test_vin = "WF0DP3TH6H4123982"


def home(request):
    """
    gets vin info from API
    """

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

# trzeba partiala zajebac z htmx
def openai_get_car_info(request):
    """
    ask chatgpt API about car with given information
    """

    if request.method == "POST":
        # Sprawdzamy czy w POST jest nasz klucz
        if "typical_issues" in request.POST:
            # Tutaj Twoja logika (np. zapytanie do OpenAI)
            message = "Znaleziono typowe usterki: Problem z pompą paliwa, wycieki oleju..."
            
            # Zwracasz TYLKO partiala. Django znajdzie go w folderze templates/partials/
            return render(request, 'partials/gpt_typical_issues_car.html', {'message': message})

    # Dla GET (pierwsze wejście) ładujesz całą stronę
    return render(request, 'home.html')


def xd(request):
    pass