# llm_processing.py
import json
import uuid
import re
from llms.llm_config import llm_config

class LLMProcessor:
    EXPECTED_FIELDS = {
        "name", "email", "phone_number", "location",
        "department", "issue", "service",
        "additional_information", "detailed_description"
    }

    def __init__(self):
        """ Initialize the LLMProcessor with necessary settings. """
    
    @staticmethod
    def extract_single_intent(response_text):
        valid_intents = [
            "Accusation", "Booking", "Information Request", 
            "General Commentary", "Complaint", "Compliment"
        ]
        pattern = r'(?:"|\')?(\b' + '|'.join(valid_intents) + r'\b)(?:"|\')?'
        match = re.search(pattern, response_text, re.IGNORECASE)
        return match.group(1) if match else "Undefined"

    @staticmethod
    def extract_sentiment(text):
        """Extracts the sentiment from a sentence by searching for specific keywords."""
        patterns = {
            'positive': re.compile(r'\b(positive|professional|polite|encouraging|good)\b', re.IGNORECASE),
            'negative': re.compile(r'\b(negative|problematic|difficult|bad)\b', re.IGNORECASE),
            'neutral': re.compile(r'\b(neutral|objective|impartial|fair)\b', re.IGNORECASE)
        }
        for sentiment, pattern in patterns.items():
            if pattern.search(text):
                return sentiment
        return 'undefined'

    def score_output(self, json_data, intent):
        score = 0
        for field in self.EXPECTED_FIELDS:
            if field in json_data:
                score += 1

        # Adjust score based on the intent
        if intent == "Undefined":
            score = max(0, score - 3)

        return score

    def extract_and_format_json(self, text_content):
        json_data = None
        try:
            json_start = text_content.find('{')
            json_end = text_content.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_string = text_content[json_start:json_end]
                json_data = json.loads(json_string)
        except json.JSONDecodeError:
            pass

        output = json_data if json_data else {}
        return output

    def extract_json_from_audio_data(self, data):
        transcription = data['transcription']
        instructions = data['text']

        # Mapping guideline keywords to phrases used in the transcription
        mappings = {
            "Name": "the full name(s) of the individual(s) involved",
            "Email": "the email address(es) cited",
            "Phone Number": "any phone number(s) provided",
            "Location": "details of any specific locations related to the issue or service",
            "Department": "the department or entity involved",
            "Issue": "a succinct description of the primary issue(s) discussed",
            "Service": "the specific service(s) referenced in relation to the issue",
            "Additional Information": "other pertinent details or stakeholders mentioned",
            "Detailed Description": "an in-depth summary of the concern or request, including desired outcomes"
        }

        # Initializing JSON object with empty fields
        extracted_info = {
            "name": "",
            "email": "",
            "phone_number": "",
            "location": "",
            "department": "",
            "issue": "",
            "service": "",
            "additional_information": "",
            "detailed_description": ""
        }

        # Extract and assign information based on the provided transcription
        for key, hint in mappings.items():
            # A simple placeholder to extract text after a specific keyword or phrase
            # This can be replaced with more complex regex patterns or NLP techniques for better accuracy
            start = transcription.find(hint)
            if start != -1:
                # Extract hypothetical substrings that follow the hint phrases.
                # This is highly simplified and may need real regex/NLP for accurate results
                end = transcription.find('.', start)
                if end != -1:
                    extracted_info[key.lower().replace(" ", "_")] = transcription[start + len(hint) + 1:end].strip()

        return json.dumps(extracted_info, indent=4)

    def process_text_and_extract_data(self, conversation_text):
        conversation_id = str(uuid.uuid4())
        response_data = llm_config.invoke(conversation_text)
        response_intent = llm_config.invoke(conversation_text, template_type='intent_classification')

        json_data = self.extract_and_format_json(response_data.get('text', '{}'))
        intent = self.extract_single_intent(response_intent.get('text', '{}'))

        response_summary = llm_config.invoke(conversation_text, template_type='summary_classification')
        response_sentiment = llm_config.invoke(conversation_text, template_type='sentiment_classification')

        summary = response_summary.get('text', '{}')
        sentiment = self.extract_sentiment(response_sentiment.get('text', '{}'))

        # Calculate the output score after processing data and intents
        output_score = self.score_output(json_data, intent)

        formatted_output = {
            "conversation_id": conversation_id,
            "conversation_text": conversation_text,
            "data": json_data,
            "intent": intent,
            "sentiment": sentiment,
            "summary": summary,
            "output_score": output_score
        }

        return json.dumps(formatted_output, indent=4)
    
    def process_audio_and_extract_data(self, transcription):
        conversation_id = str(uuid.uuid4())
        
        response_data = llm_config.invoke(transcription, template_type='audio_extraction')
        response_intent = llm_config.invoke(transcription, template_type='intent_classification')
        
        print(response_data)
        
        json_data = self.extract_json_from_audio_data(response_data.get('text', '{}'))
        intent = self.extract_single_intent(response_intent.get('text', '{}'))

        response_summary = llm_config.invoke(transcription, template_type='summary_classification')
        response_sentiment = llm_config.invoke(transcription, template_type='sentiment_classification')

        summary = response_summary.get('text', '{}')
        sentiment = self.extract_sentiment(response_sentiment.get('text', '{}'))

        # Calculate the output score after processing data and intents
        output_score = self.score_output(json_data, intent)

        formatted_output = {
            "conversation_id": conversation_id,
            "transcription": transcription,
            "data": json_data,
            "intent": intent,
            "sentiment": sentiment,
            "summary": summary,
            "output_score": output_score
        }

        return json.dumps(formatted_output, indent=4)

# Usage example:
# processor = LLMProcessor()
# result = processor.process_text_and_extract_data("Sample conversation text")
# print(result)
