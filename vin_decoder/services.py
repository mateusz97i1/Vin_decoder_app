import requests
import logging
import os
import openai
import markdown2

from django.shortcuts import render
from openai import OpenAIError
from openai import OpenAI

#We don't print in production
logger = logging.getLogger(__name__)

#gpt model with api
MODEL_GPT='gpt-5.4-mini'
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


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
        
        return car_info, None
        
        

    except requests.exceptions.Timeout as e:

        logger.exception(f"Timeout connecting to API for VIN {vin}")
        return None, "Service timed out"

    except requests.exceptions.RequestException as e:
        
        logger.exception(f"error fetching Vin data{e}")
        return None, "Can't retrieve data"


def openai_prompt_basic( car_description, system_prompt):
    """
    ask chatgpt API about car with given information
    """

    try:
        response = client.chat.completions.create(
            model = MODEL_GPT,
            messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": car_description},
        ],
            timeout= 30

        )

        results = response.choices[0].message.content

        #markdown visual edit
        results_html = markdown2.markdown(results, extras= ['break-on-newline'])

        return results_html, None

    except requests.exceptions.Timeout as e:

        logger.exception(f"found timeout error{e}")

        return None, "Try again later"
    

    except OpenAIError as e:

        logger.exception(f"error{e}")

        return None,"OpenAI error"





