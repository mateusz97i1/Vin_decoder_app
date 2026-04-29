import requests
import logging
import os
import hashlib

from django.shortcuts import render
from openai import OpenAIError
from openai import OpenAI
from django.core.cache import cache



#We don't print in production
logger = logging.getLogger(__name__)

#gpt model with api
MODEL_GPT='gpt-5.4-mini'
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
PROMPT_VERSION = "v1.0"
CACHE_TTL = 60 * 60 * 24 * 30 #30 days


def get_vehicle_data_vin(vin: str):
    """
    Fetches vehicle data from NHTSA API. 
    Returns a dict of data or a dict containing an error message.
    """
    if not vin:
        return None, "Please provide a VIN number"
    
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
        
        cache.set(cache_key, car_info, timeout= CACHE_TTL)
        
        return car_info, None
        
        

    except requests.exceptions.Timeout as e:

        logger.exception(f"Timeout connecting to API for VIN {vin}")
        return None, "Service timed out"

    except requests.exceptions.RequestException as e:
        
        logger.exception(f"error fetching Vin data{e}")
        return None, "Can't retrieve data"




def openai_prompt_basic( car_description, action):
    """
    ask chatgpt API about car with given information
    """
    
    if not action:

        error_msg = "Action parameter is missing; cannot generate OpenAI prompt."

        logger.exception(error_msg)

        return None, error_msg


    # cachaing logic
    clean_description = str(car_description).strip().lower()

    # create sha256 unique code
    hash_input= f"{PROMPT_VERSION}:{action}:{clean_description}"
    cache_key = f"call_llm{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()}"

    cached_data = cache.get(cache_key)

    if cached_data:

        return cached_data, None



    #system promt message to AI related to each button
    task_map = {
        "common_issues": "tell me about 3 typical issues with this car model",
        "price_range": "tell me the average price range for this car model in the current market",
        "millage_range": "tell me the average mileage range at which major services are usually needed for this model"
    }

    # get selected task for button
    selected_task = task_map.get(action)

    # common system prompt
    system_prompt = (
        f"You are a car enthusiast. Based on the information provided, {selected_task}. "
        "If this is a performance version (RS, M, etc.), you already know it by engine power. "
        "Don't ask questions. JUST answer directly. NO QUESTIONS AT THE END."
    )

    

    try:
        response = client.chat.completions.create(
            model = MODEL_GPT,
            messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": car_description},
        ],
            timeout= 30

        )
        # openAI reasults 
        raw_results = response.choices[0].message.content

        #save in cache
        cache.set(cache_key, raw_results, timeout= CACHE_TTL)

        return raw_results, None

    except Exception as e:

        logger.exception(f"found timeout error for {car_description}: {e}")

        return None, "Try again later"
    

    except OpenAIError as e:

        logger.exception(f"error{e}")

        return None,"OpenAI error"





