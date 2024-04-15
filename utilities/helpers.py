# helpers.py

import json
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist

def pretty_print_json(data):
    """Prints JSON data in a readable format.

    Parameters:
        data (dict or list): The JSON data to print.
    """
    return json.dumps(data, indent=4, sort_keys=True)

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

def top_words(data_json, podium=3):

    # Load data
    data = json.loads(data_json)

    # Extract textual data
    textual_content = " ".join([data['data'][key] for key in data['data'] if isinstance(data['data'][key], str)])

    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    textual_content = textual_content.translate(translator)

    # Tokenize text
    tokens = word_tokenize(textual_content, language='portuguese')

    # Remove stopwords
    stop_words = set(stopwords.words('portuguese'))
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]

    # Frequency distribution of words
    freq_dist = FreqDist(filtered_tokens)

    # Get the most common words
    keywords = freq_dist.most_common(3)

    return keywords