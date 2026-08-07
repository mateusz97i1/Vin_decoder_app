import logging
import markdown2


from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from celery.result import AsyncResult
from django.http import HttpResponse
from django.db import IntegrityError



from .forms import InputVinForm, NewsletterSubscriberForm
from .services import get_vehicle_data_vin, openai_prompt_basic
from .tasks import generate_pdf_task, join_newsletter
from . models import NewsletterSubscriber

# create logger
logger = logging.getLogger(__name__)

# bmw vin number
test_vin = "WBA5U9C00LFJ37061"



@ratelimit(key="ip", rate="30/m", block=False)
@require_GET
def home(request):
    """
    gets vehicle vin and gets it's info from NHTSA API
    """
    was_limited = getattr(request, "limited", False)
    car_info = None
    message_error = None
    vin = None
    form_vin = InputVinForm(request.GET or None)

    # when rate limiter is hit
    if was_limited:
        message_error = "You have reached refresh limit, Pleas wait 1 min to try agian."
        return render(
            request,
            "home.html",
            context={"message_error": message_error, "form_vin": form_vin},
        )

    if form_vin.is_valid():
        vin = form_vin.cleaned_data["vin_number"]
        car_info, message_error = get_vehicle_data_vin(vin)

    return render(
        request,
        "home.html",
        context={
            "car_info": car_info,
            "message_error": message_error,
            "vin": vin,
            "form_vin": form_vin,
        },
    )



@login_required
@ratelimit(key="ip", rate="3/m", block=False)
@require_POST
def openai_common_car_issues(request):
    """
    asks chatgpt API about most common car issues
    """
    was_limited = getattr(request, "limited", False)

    if was_limited:
        message_error = "You have reached refresh limit, Pleas wait 1 min to try agian."
        return render(
            request,
            "partials/gpt_typical_issues_car.html",
            context={"message_error": message_error},
        )

    # get car value
    car_description = request.POST.get("car_description", "")
    # get action button
    action = request.POST.get("action")
    vin = request.POST.get("vin", "")

    # when invalid action return errror
    if not action or not car_description:
        return render(
            request,
            "partials/gpt_typical_issues_car.html",
            {"message_error": "Invalid action"},
        )

    # get openAI response from servies,py
    raw_results, message_error = openai_prompt_basic(car_description)

    # visual edit using markdown
    results_html = markdown2.markdown(raw_results, extras=["break-on-newline"])

    # Return onlyu partial from templates/partials/
    return render(
        request,
        "partials/gpt_typical_issues_car.html",
        context={
            "results_html": results_html,
            "message_error": message_error,
            "vin": vin,
            "car_description": car_description,
        },
    )



@login_required
@require_POST
def export_vin_raport_pdf(request):
    """Generates pdf with AI generated raport. Data comes from supabase bucket"""
    action = request.POST.get("action")
    vin = request.POST.get("vin")
    car_description = request.POST.get("car_description")

    if not vin:
        logger.error("Can't get VIN")
        return redirect("vin_decoder:home")

    if action == "save_pdf":
        try:
            # Trigger celery task
            task = generate_pdf_task.delay(vin, car_description)

            # Return the loading state fragment to HTMX
            return render(
                request,
                "partials/pdf_loading.html",
                context={"task_id": task.id},
            )

        except Exception as e:
            logger.exception(f"Error during generating pdf {e}")

            return HttpResponse("Error during generating pdf.", status=500)

    return redirect("vin_decoder:home")



@login_required
@require_GET
def check_task_status(request, task_id):
    """Checks status of generated raport if it's ready to donwload"""


    res = AsyncResult(task_id)
    logger.info(f"Task {task_id} status: {res.status}")

    # If it's still processing, keep polling
    if not res.ready():
        return render(
            request,
            "partials/pdf_loading.html",
            context={"task_id": task_id, "status": res.status},
        )

    # If it succeeded, tell HTMX to stop polling and show a download link
    if res.status == "SUCCESS":
        # task returns the download URL
        download_url = res.result
        return render(
            request,
            "partials/pdf_download.html",
            context={"download_url": download_url},
        )


    # If it failed
    logger.error("Error during generating pdf url")
    return render(
        request,
        "partials/pdf_download_failed.html",
        context={"failed_info": str(res.info)},
    )


def contanct_view(request):

    return render(request, 'contact.html')


def about_us(request):

    return render(request, 'about_us.html')


def privacy_policy(request):

    return render(request, 'privacy_policy.html')


def rules(request):

    return render(request, 'rules.html')




@require_POST
def thanks_for_newsletter_subscription(request):
    """Validates email and, if valid, shows thanks + queues welcome email via celery"""

    email_form = NewsletterSubscriberForm(request.POST)

    if email_form.is_valid():
        email_adress = email_form.cleaned_data['send_email_to']

        try:
            NewsletterSubscriber.objects.create(email=email_adress)
        except IntegrityError:
            return render(
                request,
                'partials/newsletter_block.html',
                context={
                    'success': False,
                    'email_form': email_form,
                    'error': 'This email has been already used.',
                },
            )

        join_newsletter.delay(email_adress)
        return render(
            request,
            'partials/newsletter_block.html',
            context={'success': True, 'email': email_adress},
        )

    else:
        logger.warning(f"Error- can't issue newsletter subscription: {email_form.errors}")
        return render(
            request,
            'partials/newsletter_block.html',
            context={'success': False, 'email_form': email_form}
        )