# helpers.py

import json
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import requests

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

def transcribe_audio(tts_server, file_path):
    """
    Sends a POST request to a local server to transcribe a WAV file.

    Args:
        file_path (str): The path to the .wav audio file to be transcribed.

    Returns:
        str: The transcribed text from the audio file.
    """

    url = (f"{tts_server}/transcribe")
    files = {'audio': (file_path, open(file_path, 'rb'), 'audio/wav')}

    try:
        response = requests.post(url, files=files)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX, 5XX)

        # Assuming the response body contains the transcript directly
        return response.text
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"OOps: Something Else: {err}")
    finally:
        files['audio'][1].close()  # Ensure the file is closed after the request
