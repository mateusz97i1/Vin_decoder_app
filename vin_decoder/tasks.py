import logging
import markdown2
import smtplib
import socket

from celery import shared_task
from django.template.loader import render_to_string
from django.conf import settings
from supabase import create_client, Client
from celery.exceptions import SoftTimeLimitExceeded
from django.core.mail import EmailMultiAlternatives, send_mail

from .utils import generate_car_raport_pdf, get_raport_data_from_redis
from .services import get_ready_report_url_supabase_db
from .models import MetadataRaports


logger = logging.getLogger(__name__)

supabase : Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


@shared_task(
    soft_time_limit=15,
    time_limit=30,
    queue='generate_pdf',
)
def generate_pdf_task(vin, car_description):

    #replace spaces with floor for better reading
    clean_car_description = str(car_description).strip().upper().replace(" ","_")


    try:

        #if raport already exists get url from db:
        report_url_db= get_ready_report_url_supabase_db(clean_car_description)
        if report_url_db:
            logger.info("got url from db")
            return report_url_db

        #mark status as processing as we are actually generating
        MetadataRaports.objects.update_or_create(
            car_model=clean_car_description,
            defaults={'status':'PROCESSING'}
        )


        #get raport from cache
        raw_info_data = get_raport_data_from_redis(car_description)

        if not raw_info_data:
            logger.error(f"Cache miss for data: {car_description}")
            raise ValueError(f"Cache miss - no report data found in Redis for: {car_description}")
        
        #visual edit using markdown
        car_info_data = markdown2.markdown(raw_info_data, extras= ['break-on-newline'])

        #use html template to generate pdf file  
        html_string = render_to_string('pdf_render/car_raport_pdf.html', context={
            'raport_html': car_info_data,
            'vin': vin
        })
        
        pdf_file = generate_car_raport_pdf(html_content= html_string)

        #change pdf to bytes as supabase requiers
        pdf_file.seek(0)
        pdf_bytes = pdf_file.getvalue()
        
        file_name = f"report_{clean_car_description}.pdf"

        
        #upload pdf to supabsae
        supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
            path=file_name,
            file=pdf_bytes,
            file_options={
            'upsert': 'true',
            "content-type": "application/pdf"
            })

        
        #retrieve URL donwload
        download_url_public = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(
            file_name,
            {"download": True})

        logger.info(f"Public URL generated: {download_url_public}")

        #Save download_url_public into database!
        MetadataRaports.objects.update_or_create(
            car_model= clean_car_description,
            defaults={
                'status': 'SUCCESS',
                'supabase_url':download_url_public
            },
        )
        
        return download_url_public

    except SoftTimeLimitExceeded:
        logger.warning(f"Task generating pdf for {vin} was shout. Exceeded soft_time_limit (15s).")

        #mark status as failrue in db
        MetadataRaports.objects.update_or_create(
            car_model= clean_car_description,
            defaults={'status':'FAILURE'}
        )
        raise  


    except Exception as e:
        logger.exception(f"Error during uploading file to supabase or genereting public URL: {e}")

        #mark status as failrue in db
        MetadataRaports.objects.update_or_create(
            car_model= clean_car_description,
            defaults={'status':'FAILURE'}
        )
        raise



@shared_task(
    bind= True,
    retry_kwargs={'max_retries': 5},
    retry_backoff = True,
    retry_backoff_max = 100,
    rate_limit='4/m',
    queue='emails'
)
def send_async_email(self, email_data):
    "Send Async email using celery and django email backend"



    msg = EmailMultiAlternatives(
        subject=email_data.get('subject', ''),
        body=email_data.get('body', ''),
        from_email=email_data.get('from_email'),
        to=email_data.get('to', []),
        cc=email_data.get('cc', []),
        bcc=email_data.get('bcc', []),
        headers=email_data.get('headers', {}),
    )

    #Attach html if exists
    html_content = email_data.get('html_body')

    if html_content:
        msg.attach_alternative(html_content,"text/html")


    try:
        msg.send()

    except (smtplib.SMTPException, socket.error) as e:
        logger.error(f"Smpt error sending email{e}")
        raise self.retry(exc=e)

    except Exception as e:
        logger.error(f'Error during sending error {e}')
        raise



@shared_task(
    bind= True,
    autoretry_for=(smtplib.SMTPException, socket.error),
    retry_kwargs={'max_retries': 5},
    retry_backoff = True,
    retry_backoff_max = 100,
    rate_limit='4/m',
    queue='newsletter_join_email'
)
def join_newsletter(self, receiver_email):

    """Sends greating email for joining to newsletter"""

    try:

        send_mail(
            subject = "Vinex Newsletter",
            message = "Thank You for Subscribing to our newsletter",
            from_email = None,
            recipient_list = [receiver_email],
            fail_silently= False

        )

    except Exception as e:
        logger.error(f'Error during sending error {e}')
        raise