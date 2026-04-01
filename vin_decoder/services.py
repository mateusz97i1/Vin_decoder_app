import requests
# // write try block
def get_vehicle_data_vin(vin):

    if vin:
        url = f'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValues/{vin}?format=json'
        r = requests.get(url)
        data = r.json()
        car_info = data['Results'][0] if data.get('Results') else {}


    return car_info	