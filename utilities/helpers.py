# helpers.py

import json

# Define the expected fields in a set for easy comparison
EXPECTED_FIELDS = {
    "name", "email", "phone_number", "location",
    "department", "issue", "service",
    "additional_information", "detailed_description"
}

def score_output(json_data):
    """
    Scores the output based on the number of expected fields present in the JSON data.

    Parameters:
        json_data (dict): The JSON data parsed into a Python dictionary.

    Returns:
        int: The score representing the number of expected fields present.
    """
    # Extract keys from json_data and convert them to lowercase for case-insensitive comparison
    received_fields = set(key.lower() for key in json_data.keys())

    # Calculate the score as the count of expected fields that are present
    score = len(EXPECTED_FIELDS.intersection(received_fields))
    return score

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

    # Attempt to parse JSON from the response
    json_data = None
    json_start = text_content.find('{')
    json_end = text_content.rfind('}') + 1
    if json_start != -1 and json_end != -1:
        try:
            json_string = text_content[json_start:json_end]
            json_data = json.loads(json_string)
        except json.JSONDecodeError:
            json_data = None

    # Prepare final JSON output
    output = {}
    if json_data:
        output['data'] = json_data
        output['output_score'] = score_output(json_data)
    else:
        output['llm_output'] = text_content  # Include raw output if JSON parsing fails
        output['output_score'] = 0  # No fields match when no JSON is detected

    return json.dumps(output, indent=4)  # Return formatted JSON string



