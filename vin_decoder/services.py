import requests
import logging
import os
import hashlib
import redis

from django.shortcuts import render
from openai import OpenAIError
from openai import OpenAI
from django.core.cache import cache
from django.conf import settings
from typing import Optional

from .models import MetadataRaports


#We don't print in production
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))



def get_vehicle_data_vin(vin: str):
    """
    Fetches vehicle data from NHTSA API. 
    Returns a dict of data or a dict containing an error message.
    """
    if not vin:
        return None, "Please provide a VIN number"

    #get mandatory settings
    cache_ttl = settings.CACHE_TTL
    
    vin = vin.strip().upper()  # Ensure VIN is in the correct format
    url= os.getenv('NHTSA_API_URL') + vin
    


    if len(vin) != 17:
        return None, "Incorrect Vin number"

    # caching logic for vin
    cache_key = f"vin_cache{vin}"

    cached_data = cache.get(cache_key)

    if cached_data:

        return cached_data, None


    try:
        
        response = requests.get(
            url,
            params={'format': 'json'},
            timeout= 10
            )
        
        
        response.raise_for_status()

        data = response.json()

        results = data.get('Results', [])

        if not results:
            return None, "No data found"
        
        car_info = results[0]


        error_code = str(car_info.get('ErrorCode', '0'))
        if error_code != '0':
            error_text = car_info.get('ErrorText', 'Unknown API Error')
            logger.warning(f"NHTSA rejected VIN {vin}: {error_text}")
            return None, f"Invalid VIN data: {error_text}"
        
        cache.set(cache_key, car_info, timeout= cache_ttl)
        
        return car_info, None
        
        

    except requests.exceptions.Timeout as e:

        logger.exception(f"Timeout connecting to API for VIN {vin}")
        return None, "Service timed out"

    except requests.exceptions.RequestException as e:
        
        logger.exception(f"error fetching Vin data{e}")
        return None, "Can't retrieve data"



def openai_prompt_basic( car_description):
    """
    ask chatgpt API about car with given information
    """
    #get mandatory settings
    prompt_version = settings.PROMPT_VERSION
    model_gpt = settings.MODEL_GPT
    cache_ttl = settings.CACHE_TTL
    
    
    if not car_description :

        error_msg = "Car description parameter is missing; cannot generate OpenAI prompt."

        logger.exception(error_msg)

        return None, error_msg


    # cachaing logic
    clean_car_description = str(car_description).strip().upper()

    # create sha256 unique code
    hash_input= f"{prompt_version}:{clean_car_description}"
    cache_key = f"call_llm{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()}"

    cached_data = cache.get(cache_key)

    if cached_data:

        return cached_data, None
    

    # common system prompt
    system_prompt = (
        "You are a car enthusiast. Based on the information provided, generate a comprehensive report including:\n"
        "1. 3 typical issues with this car model.\n"
        "2. The average price range for this car model in the current market.\n"
        "3. The average mileage range at which major services are usually needed for this model.\n"
        "If this is a performance version (RS, M, etc.), you already know it by engine power. Don't tell that indicates on that or this specific model "
        "Don't ask questions. Don't suggest anything at the end of the raport. JUST answer directly. NO QUESTIONS AT THE END."
    )

    

    try:
        response = client.chat.completions.create(
            model = model_gpt,
            messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": car_description},
        ],
            timeout= 30,
            max_completion_tokens= 850

        )
        # openAI reasults 
        raw_results = response.choices[0].message.content

        #save in cache
        cache.set(cache_key, raw_results, timeout= cache_ttl)

        return raw_results, None

    except Exception as e:

        logger.exception(f"found timeout error for {car_description}: {e}")

        return None, "Try again later"
    

    except OpenAIError as e:

        logger.exception(f"error{e}")

        return None,"OpenAI error"




def get_ready_report_url_supabase_db(car_description: str) -> Optional[str]:
    "Get url to the car report only if status is :completed"


    clean_car_description = str(car_description).strip().upper().replace(" ","_")

    #filter reports
    report = MetadataRaports.objects.filter(car_model = clean_car_description,
                                            status = 'COMPLETED'
).only('supabase_url').first()
    

    if report:

        return report.supabase_url
