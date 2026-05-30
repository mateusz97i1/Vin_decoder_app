import io
import logging
import hashlib
import markdown2

from xhtml2pdf import pisa
from django.core.cache import cache
from django.conf import settings

#create logger
logger = logging.getLogger(__name__)


def generate_car_raport_pdf(html_content):
    """Take generated raport in memory and save it as pdf using xhtml2pdf"""

    pisa.showLogging()

    output = io.BytesIO()

#  create pdf in memory
    pisa_status = pisa.CreatePDF(
        html_content,
        dest= output,
        encoding='utf-8'
    )

    if pisa_status.err:
        logger.error(f"Error saving PDF: {pisa_status.err}")
        return None

    # set cursor in memory at the beggining
    output.seek(0)

    # return file with according name, file extension (forces download in web browser) 
    return output



def get_raport_data_from_redis(car_description):
    #AI model version
    prompt_version = settings.PROMPT_VERSION

    if not car_description:

        logger.error(f"Can't get Car description {car_description}")
        return None

    clean_car_description = str(car_description).strip().upper()

    # create sha256 unique code
    hash_input= f"{prompt_version}:{clean_car_description}"
    cache_key = f"call_llm{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()}"

    try:

        cached_data = cache.get(cache_key)

    except Exception as e:

        logger.error(f"Error getting cached data {e}")
        return None


    return cached_data
