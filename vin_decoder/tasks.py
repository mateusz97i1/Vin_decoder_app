import logging
import markdown2

from celery import shared_task
from django.template.loader import render_to_string
from django.conf import settings
from supabase import create_client, Client

from .utils import generate_car_raport_pdf, get_raport_data_from_redis



logger = logging.getLogger(__name__)

supabase : Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


@shared_task
def generate_pdf_task(vin, car_description):

    try:

        #get raport from cache
        raw_info_data = get_raport_data_from_redis(car_description)

        if not raw_info_data:
            logger.error(f"Cache miss for data: {car_description}")
            return None
        
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

        file_name = f"raport_VIN_{vin}.pdf"

        logger.info(f"Uploading PDF to Supabase: {file_name}")
        
        #upload pdf to supabsae
        supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
            path=file_name,
            file=pdf_bytes,
            file_options={
            'upsert': 'true',
            "content-type": "application/pdf"
            })

        logger.info(f"PDF uploaded successfully, getting public URL")
        
        #retrieve URL donwload
        download_url_public = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(
            file_name,
            {"download": True})

        logger.info(f"Public URL generated: {download_url_public}")
        
        return download_url_public

    except Exception as e:

        logger.exception(f"Error during uploading file to supabase or genereting public URL: {e}")
        return None
