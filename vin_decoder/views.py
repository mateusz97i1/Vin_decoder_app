import logging
import markdown2


from django.shortcuts import render , redirect
from django.views.decorators.http import require_POST, require_GET
from django_ratelimit.decorators import ratelimit 
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from celery.result import AsyncResult
from django.http import HttpResponse


from .forms import InputVinForm
from .services import get_vehicle_data_vin, openai_prompt_basic
from .tasks import generate_pdf_task

#create logger
logger = logging.getLogger(__name__)

#bmw vin number
test_vin = "WBA5U9C00LFJ37061"

@ratelimit(key='ip', rate='30/m',  block= False)
@require_GET
def home(request):
    """
    gets vehicle vin and gets it's info from NHTSA API
    """
    was_limited = getattr(request, 'limited', False)
    car_info = None
    message_error = None
    vin = None
    form_vin =InputVinForm(request.GET or None)

    # when rate limiter is hit
    if was_limited:
        message_error = "You have reached refresh limit, Pleas wait 1 min to try agian."
        return render(request, 'home.html', context={
            'message_error': message_error,
            'form_vin': form_vin
        })

    if form_vin.is_valid():

        vin = form_vin.cleaned_data['vin_number']
        car_info, message_error = get_vehicle_data_vin(vin)


    return render(request, 'home.html',context= {
        'car_info': car_info,
        'message_error': message_error,
        'vin': vin,
        'form_vin':form_vin
        })


# @login_required
@ratelimit(key='ip', rate='3/m', block= False)
@require_POST
def openai_common_car_issues(request):
    """
    asks chatgpt API about most common car issues
    """
    was_limited = getattr(request, 'limited', False)

    if was_limited:
        message_error = "You have reached refresh limit, Pleas wait 1 min to try agian."
        return render(request, 'partials/gpt_typical_issues_car.html', context={
            'message_error': message_error
        })

    # get car value
    car_description = request.POST.get("car_description", "")
    # get action button
    action = request.POST.get("action")
    vin = request.POST.get("vin", "")

    #when invalid action return errror
    if not action or not car_description:
        return render(request, 'partials/gpt_typical_issues_car.html', 
                      {'message_error': "Invalid action"})


    #get openAI response from servies,py
    raw_results, message_error = openai_prompt_basic(car_description)

    #visual edit using markdown
    results_html = markdown2.markdown(raw_results, extras= ['break-on-newline'])


            
    # Return onlyu partial from templates/partials/
    return render(request, 'partials/gpt_typical_issues_car.html', 
                    context= {
                    'results_html': results_html,
                    'message_error': message_error,
                    'vin': vin,
                    'car_description':car_description,
                    })



@require_POST
def export_vin_raport_pdf(request):

    """Generates pdf with AI generated raport. Data comes from supabase bucket"""

    action = request.POST.get('action')
    vin = request.POST.get('vin')
    car_description = request.POST.get('car_description')

    if not vin:
        logger.error("Can't get VIN")

        return redirect('vin_decoder:home')


    # button: generates pdf raport and returns it as response, otherwise return to home page
    if action == "save_pdf":

        try:
            # Trigger celery task
           task = generate_pdf_task.delay(vin,car_description)

           return render(request,'partials/pdf_loading.html',
                         context={'task': task})
        
        except Exception as e:

            message_error = "Error during generating pdf."
            logger.exception(f"Error during generating pdf {e}")

            return render(request, 'home.html', context={'message_error':message_error})

    return render(request, 'home.html')



@require_GET
def check_task_status(request, task_id):
    res = AsyncResult(task_id)
    
    logger.info(f"Task {task_id} status: {res.status}")
    pass