import requests
import logging

#We don't print in production
logger = logging.getLogger(__name__)

def get_vehicle_data_vin(vin: str):
    """
    Fetches vehicle data from NHTSA API. 
    Returns a dict of data or a dict containing an error message.
    """
    vin = vin.strip().upper()  # Ensure VIN is in the correct format

    if not vin:
        return None, "Please provide a VIN number"


    if len(vin) != 17:
        return None, "Incorrect Vin number"


    try:
        url = f'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValues/{vin}?format=json'
        response = requests.get(url,timeout= 10)
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

