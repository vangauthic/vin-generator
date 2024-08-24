import random
from vininfo import Vin
import requests
import re

wmi_codes = {
    'Lexus': ['JTH', '2T2'],
    'Toyota': ['JT2', '4T1'],
    'Ford': ['1FA', '2FM'],
    'Chevrolet': ['1GC', '3GC'],
    'BMW': ['WBA', 'WBX'],
    'Mercedes': ['WDB', '4JG'],
}

vds_patterns = {
    'Lexus': ['BL46F', 'GF10F', 'GF40L', 'GF50L', 'KF25L', 'LA250', 'LC300', 'LM350'],
    'Toyota': ['BU40L', 'FV50R', 'GV70F', 'KU45L'],
    'Ford': ['PU3EL', 'MV5LT', 'RV6JT'],
    'Chevrolet': ['CU1FL', 'FU2MT', 'HU4GR'],
    'BMW': ['XY34F', 'PL55G', 'GL56H'],
    'Mercedes': ['FJ3KL', 'LJ7RM', 'NJ8TS'],
}

year_codes = {
    2001: '1', 2002: '2', 2003: '3', 2004: '4', 2005: '5', 2006: '6', 2007: '7',
    2008: '8', 2009: '9', 2010: 'A', 2011: 'B', 2012: 'C', 2013: 'D', 2014: 'E',
    2015: 'F', 2016: 'G', 2017: 'H', 2018: 'J', 2019: 'K', 2020: 'L', 2021: 'M',
    2022: 'N', 2023: 'P', 2024: 'R'
}

plant_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

def calculate_check_digit(vin):
    weights = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
    transliterations = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'J': 1, 'K': 2, 'L': 3, 'M': 4,
        'N': 5, 'P': 7, 'R': 9, 'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9,
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '0': 0
    }

    total = 0
    for i in range(17):
        if vin[i] in transliterations:
            value = transliterations[vin[i]]
        else:
            value = int(vin[i])
        total += value * weights[i]
    
    remainder = total % 11
    if remainder == 10:
        return 'X'
    else:
        return str(remainder)

def generate_vin():
    manufacturer = random.choice(list(wmi_codes.keys()))
    wmi = random.choice(wmi_codes[manufacturer])
    
    vds = random.choice(vds_patterns[manufacturer])
    
    check_digit = '0'
    
    year = random.choice(list(year_codes.values()))
    plant = random.choice(plant_codes)
    serial_number = ''.join(random.choices('0123456789', k=6))
    
    vin_without_check_digit = wmi + vds + check_digit + year + plant + serial_number
    
    check_digit = calculate_check_digit(vin_without_check_digit)
    
    vin = wmi + vds + check_digit + year + plant + serial_number
    return vin

def get_model_year_and_model(vin):
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
    response = requests.get(url)
    data = response.json()

    model_year = data['Results'][0].get('ModelYear', 'Unknown')
    model = data['Results'][0].get('Model', 'Unknown')
    
    if model == 'Unknown' or model_year == 'Unknown':
        url_alt = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
        response_alt = requests.get(url_alt)
        data_alt = response_alt.json()
        
        for result in data_alt['Results']:
            if result.get('ModelYear'):
                model_year = result['ModelYear']
            if result.get('Model'):
                model = result['Model']

    return model_year, model

def continuously_generate_vins():
    count = 0
    with open("checked_vins.txt", "w") as file:
        try:
            while count < 20:
                new_vin = generate_vin()
                try:
                    vehicle = Vin(new_vin)
                    if vehicle:
                        model_year, model = get_model_year_and_model(new_vin)
                        brand = str(vehicle.brand).replace("Brand", "Brand:")
                        brand = brand.replace(')', '')
                        brand = brand.replace('(', '')
                        if model is not None and model != '':
                            file.write(f"Valid VIN: {new_vin}\n")
                            file.write(f"{brand}\n")
                            file.write(f"Country: {vehicle.country}\n")
                            file.write(f"Model: {model}\n")
                            file.write(f"Model Year: {model_year}\n")
                            file.write('\n')
                            file.flush()
                            print(f'Write {count + 1}')
                            
                            count += 1
                    else:
                        print("Invalid VIN generated.\n")
                except Exception as e:
                    print(f"An error occurred: {e}\n")
            print("20 VINs generated and validated.\n")
        except KeyboardInterrupt:
            print("VIN generation stopped.\n")

continuously_generate_vins()
