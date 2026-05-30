import logging
import markdown2

from celery import shared_task
from django.template.loader import render_to_string
from django.conf import settings
from supabase import create_client, Client

from .utils import generate_car_raport_pdf, get_raport_data_from_redis



logger = logging.getLogger(__name__)

supabase : Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)