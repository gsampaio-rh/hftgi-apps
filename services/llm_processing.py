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

    def process_text_and_extract_data(self, conversation_text):
        conversation_id = str(uuid.uuid4())
        response_data = llm_config.invoke(conversation_text)
        response_intent = llm_config.invoke(conversation_text, template_type='intent_classification')
    
        json_data = self.extract_and_format_json(response_data.get('text', '{}'))
        intent = self.extract_single_intent(response_intent.get('text', '{}'))

        # Calculate the output score after processing data and intents
        output_score = self.score_output(json_data, intent)

        formatted_output = {
            "data": json_data,
            "conversation_id": conversation_id,
            "intent": intent,
            "output_score": output_score
        }

        return json.dumps(formatted_output, indent=4)

# Usage example:
# processor = LLMProcessor()
# result = processor.process_text_and_extract_data("Sample conversation text")
# print(result)