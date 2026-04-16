import openai
from django.views.decorators.http import require_POST, require_GET
import os
import requests
import logging
import markdown2
import io

from .forms import InputVinForm
from django.shortcuts import render , redirect
from .services import get_vehicle_data_vin, openai_prompt_basic
from xhtml2pdf import pisa
from django.http import FileResponse

#create logger
logger = logging.getLogger(__name__)

#focus rs vin number
test_vin = "WBA5U9C00LFJ37061"


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


def save_reasults_pdf(html_source,car_description):
    """Take generated raport in memory and save it as pdf using xhtml2pdf"""

    pisa.showLogging()

    output = io.BytesIO()

#  create pdf in memory
    pisa_status = pisa.CreatePDF(
        html_source,
        dest= output
    )

    if pisa_status.err:
        logger.error(f"Error saving PDF: {pisa_status.err}")

    # set cursor in memory at the beggining
    output.seek(0)

    # return file with according name, file extension (forces download in web browser) 
    return FileResponse(
        output,
        as_attachment= True,
        filename= f"Raport+{car_description}.pdf"
    )


@require_POST
def openai_common_car_issues(request):
    """
    ask chatgpt API about most common car issues
    """

    # get car value
    car_description = request.POST.get("typical_issues", "")
    # get action button
    action = request.POST.get("action")


    #system promt message to AI related to each button
    task_map = {
        "common_issues": "tell me about 3 typical issues with this car model",
        "price_range": "tell me the average price range for this car model in the current market",
        "millage_range": "tell me the average mileage range at which major services are usually needed for this model",
        "save_pdf": "provide detailed information about this car model"
    }

    # get selected task for button
    selected_task = task_map.get(action)
    if not selected_task or not car_description:
        return render(request, 'partials/gpt_typical_issues_car.html', 
                      {'message_error': "Invalid action"})
    

    
    # common system prompt
    system_prompt = (
        f"You are a car enthusiast. Based on the information provided, {selected_task}. "
        "If this is a performance version (RS, M, etc.), you already know it by engine power. "
        "Don't ask questions. JUST answer directly. NO QUESTIONS AT THE END."
    )


    results_html, message_error = openai_prompt_basic(car_description, system_prompt)

    if action == "save_pdf":

       pdf_response =  save_reasults_pdf(results_html,car_description)

       if pdf_response:
           
           return pdf_response

            
    # Return onlyu partial from templates/partials/
    return render(request, 'partials/gpt_typical_issues_car.html', 
                    context= {
                    'results_html': results_html,
                    'message_error': message_error,
                    'car_description': car_description
                    })
            
