import openai
from django.views.decorators.http import require_POST
import os
import requests
import logging
import markdown2

from .forms import InputVinForm
from django.shortcuts import render , redirect
from .services import get_vehicle_data_vin


#create logger
logger = logging.getLogger(__name__)

#focus rs vin number
test_vin = "WF0DP3TH6H4123982"

#gpt model with api
MODEL_GPT='gpt-5.4-mini'
openai_api_key= os.getenv('OPENAI_API_KEY')


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


@require_POST
def openai_get_car_info(request):
    """
    ask chatgpt API about car with given information
    """

    if request.method == "POST":
        #Check if our key is in post 
        if "typical_issues" in request.POST:
            #get car value
            car_description = request.POST.get("typical_issues", "")

            if car_description:

                #system promt message to AI
                system_prompt = """
                                U are, a car ethusiasd, with given information tell me about
                                  3 typical issues with this car model:
                                """

                try:
                    response = openai.chat.completions.create(
                        model = MODEL_GPT,
                        messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": car_description},
                    ],
                        timeout= 30

                    )

                    results = response.choices[0].message.content

                    #markdown visual edit
                    results_html = markdown2.markdown(results, extras= ['break-on-newline'])

                    #create message for user abt typical issues
                    message = f"The typical issues for {car_description} are as follows:"

                except requests.exceptions.Timeout as e:

                    logger.exception(f"found timeout error{e}")
                    message_error = "Try again later"

                    return render(request, 'partials/gpt_typical_issues_car.html', {'message_error': message_error})
                    
                    # Return onlyu partial from templates/partials/
                return render(request, 'partials/gpt_typical_issues_car.html', {'message': message,
                                                                                'results_html': results_html
                                                                                })