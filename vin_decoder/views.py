import openai
import os
import requests
import logging
import io
import markdown2

from .forms import InputVinForm
from django.shortcuts import render , redirect
from .services import get_vehicle_data_vin, openai_prompt_basic
from xhtml2pdf import pisa
from django.http import FileResponse
from .utils import generate_car_raport_pdf
from django.views.decorators.http import require_POST, require_GET


#create logger
logger = logging.getLogger(__name__)

#bmw vin number
test_vin = "WBA5U9C00LFJ37061"


# @require_GET
def home(request):
    """
    gets vehicle vin and gets it's info from NHTSA API
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
    asks chatgpt API about most common car issues
    """

    # get car value
    car_description = request.POST.get("typical_issues", "")
    # get action button
    action = request.POST.get("action")
    vin = request.POST.get("vin", "")

    #when invalid action return errror
    if not action or not car_description:
        return render(request, 'partials/gpt_typical_issues_car.html', 
                      {'message_error': "Invalid action"})


    #get openAI response from servies,py
    raw_results, message_error = openai_prompt_basic(car_description, action)

    #visual edit using markdown
    results_html = markdown2.markdown(raw_results, extras= ['break-on-newline'])


            
    # Return onlyu partial from templates/partials/
    return render(request, 'partials/gpt_typical_issues_car.html', 
                    context= {
                    'results_html': results_html,
                    'message_error': message_error,
                    'vin': vin
                    })


def export_vin_raport_pdf(request):

    """Generates pdf with AI generated raport"""

    action = request.POST.get('action')
    results_html = request.POST.get('ai_analysis')#AI generated raport
    vin = request.POST.get('vin')

    #when button clicked generate pdf with raport and return it as response, otherwise return to home page
    if action == "save_pdf":

        pdf_file = generate_car_raport_pdf(html_content= results_html)

        return FileResponse(
            pdf_file,
            as_attachment= True,
            filename=f"raport_VIN_{vin}.pdf",
            content_type= "application/pdf"
        )

    return render(request, 'vin_decoder:home')
            
