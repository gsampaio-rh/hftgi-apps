# helpers.py

from llms.llm_config import llm_config
import uuid
import json
import re

# Define the expected fields in a set for easy comparison
EXPECTED_FIELDS = {
    "name", "email", "phone_number", "location",
    "department", "issue", "service",
    "additional_information", "detailed_description"
}

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

def score_output(json_data):
    """
    Scores the output based on the number of expected fields present and non-empty.

    Parameters:
        json_data (dict): The JSON data parsed into a Python dictionary.

    Returns:
        int: The score representing the number of expected fields that are present and non-empty.
    """
    score = 0
    for field in EXPECTED_FIELDS:
        # Check if the field is present in the JSON data and it is not empty
        if field in json_data and json_data[field].strip():
            score += 1
    return score

def extract_single_intent(response_text):
    """
    Extracts the first valid intent from the model's response text, ensuring it is clean and contains only the category name.
    """
    # Define a list of all valid intents
    valid_intents = [
        "Accusation", "Booking", "Information Request", 
        "General Commentary", "Complaint", "Compliment"
    ]

    # Use regex to find the first occurrence of any valid intent in the response, accounting for potential quotes and extraneous text
    pattern = r'(?:"|\')?(\b' + '|'.join(valid_intents) + r'\b)(?:"|\')?'
    match = re.search(pattern, response_text, re.IGNORECASE)
    if match:
        return match.group(1)  # Return the matched intent without any quotes
    return "Undefined"  # Return Undefined if no valid intent is found

def extract_and_format_json(text_content):
    """
    Extracts JSON from provided text content and formats it into a structured JSON output.

    Parameters:
        text_content (str): The text content possibly containing JSON data.

    Returns:
        str: A structured JSON string with extracted data and scores.
    """
    json_data = None
    json_start = text_content.find('{')
    json_end = text_content.rfind('}') + 1
    if json_start != -1 and json_end != -1:
        try:
            json_string = text_content[json_start:json_end]
            json_data = json.loads(json_string)
        except json.JSONDecodeError:
            json_data = None

    output = {}
    if json_data:
        output['data'] = json_data
        output['output_score'] = score_output(json_data)  # Assumes presence of a scoring function
    else:
        output['llm_output'] = text_content  # Raw output if JSON parsing fails
        output['output_score'] = 0  # Indicates no valid JSON data was found

    return json.dumps(output, indent=4)

def process_text_and_extract_data(conversation_text):
    """
    Processes the given conversation text using LLM configuration,
    generates a unique conversation ID, extracts the 'text' field, and formats it.
    It also classifies the intent of the conversation and adjusts the score if no intent is found.

    Parameters:
        conversation_text (str): The conversation text to be processed.

    Returns:
        str: The processed and formatted output as JSON, including a unique conversation ID and intent.
    """
    # Generate a unique identifier for the conversation
    conversation_id = str(uuid.uuid4())

    # Invoke the LLM to process the conversation and extract necessary details
    response_data = llm_config.invoke(conversation_text)
    response_intent = llm_config.invoke(conversation_text, template_type='intent_classification')
    
    # Extract the 'text' content from the responses
    llm_data_text_output = response_data.get('text', '{}')
    llm_intent_text_output = response_intent.get('text', '{}')
    
    # Format the data output into JSON
    formatted_output = extract_and_format_json(llm_data_text_output)
    intent = extract_single_intent(llm_intent_text_output)
    
    # Append the conversation ID and intent to the formatted output JSON
    output_json = json.loads(formatted_output)
    output_json['conversation_id'] = conversation_id  # Add the generated ID to the JSON output
    output_json['intent'] = intent  # Add the intent to the JSON output

    # Adjust score if no valid intent is found
    if intent == "Undefined":
        if output_json['output_score'] > 2:  # Ensure score does not go negative
            output_json['output_score'] -= 3
        else:
            output_json['output_score'] = 0

    return json.dumps(output_json, indent=4)  # Return the updated JSON string with the conversation ID and intent
