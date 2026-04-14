import openai
from django.views.decorators.http import require_POST, require_GET
import os
import requests
import logging
import markdown2

from .forms import InputVinForm
from django.shortcuts import render , redirect
from .services import get_vehicle_data_vin, openai_prompt_basic


#create logger
logger = logging.getLogger(__name__)

#focus rs vin number
test_vin = "WF0DP3TH6H4123982"


@require_GET
def home(request):
    """
    gets vin info from API
    """

    car_info = None
    message_error = None
    vin = None
    form_vin =InputVinForm(request.GET or None)

    if form_vin.is_valid():

        vin = form_vin.cleaned_data['vin_number']
        car_info, message_error = get_vehicle_data_vin(vin)


    return render(request, 'home.html',context= {
        'car_info': car_info,
        'message_error': message_error,
        'vin': vin,
        'form_vin':form_vin
        })


@require_POST
def openai_common_car_issues(request):
    """
    ask chatgpt API about most common car issues
    """

    #system promt message to AI
    system_prompt =  "U are, a car ethusiasd, with given information tell me about 3 typical issues with this car model:"

    
    car_description = request.POST.get("typical_issues", "")

    #Check if our key is in post 
    if not car_description:

        return render(request, 'partials/gpt_typical_issues_car.html', {'message_error': "No data to analyze"})
        
    results_html , message_error = openai_prompt_basic(car_description, system_prompt)

    #create message for user abt typical issues
    message = f"The typical issues for {car_description} are as follows:"
            
        # Return onlyu partial from templates/partials/
    return render(request, 'partials/gpt_typical_issues_car.html', 
                    context= {
                    'message': message,
                    'results_html': results_html,
                    'message_error': message_error
                    })
            
