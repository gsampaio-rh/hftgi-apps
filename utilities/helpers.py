# helpers.py

import json
import re

def pretty_print_json(data):
    """Prints JSON data in a readable format.
    
    Parameters:
        data (dict or list): The JSON data to print.
    """
    print(json.dumps(data, indent=4, sort_keys=True))

def convert_keys_to_snake_case(data):
    """Converts all keys in a dictionary to snake_case, useful for JSON object keys.
    
    Parameters:
        data (dict): The dictionary whose keys need to be converted to snake_case.
        
    Returns:
        dict: A new dictionary with all keys converted to snake_case.
    """
    def to_snake_case(s):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

    if isinstance(data, dict):
        return {to_snake_case(key): convert_keys_to_snake_case(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_keys_to_snake_case(item) for item in data]
    else:
        return data

def validate_email(email):
    """Validates an email address to ensure it meets a basic standard of email format.
    
    Parameters:
        email (str): The email address to validate.
        
    Returns:
        bool: True if the email is valid, False otherwise.
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None
