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

    if request.method == "POST":

        print(request.POST)

        if "typical_issues" in request.POST:

            print("typical iussewerwerw5r444444444444444444sr")



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

        print(request.POST)

        if "typical_issues" in request.POST:

            print("typical iussewerwerw5r444444444444444444sr")

