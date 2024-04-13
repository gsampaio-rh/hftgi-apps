# helpers.py

import json

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
    import re
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
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def process_conversation(text_content):
    """ Process the conversation using the LLM and output structured information. """

    # Attempt to extract and parse JSON from the response
    try:
        # Assuming the JSON object starts with '{' and ends with '}'
        json_start = text_content.find('{')
        json_end = text_content.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            json_string = text_content[json_start:json_end]
            json_data = json.loads(json_string)  # Parse the JSON string into a Python dictionary
            return(json_data)
        else:
            print("No JSON data found in the response.")
    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)


