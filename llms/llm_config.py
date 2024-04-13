# ai_model.py

from langchain.llms import HuggingFaceTextGenInference
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from config.config_manager import config

template = """
    As an AI expert assistant, your task is to analyze the provided conversation and directly extract and format specific information into a structured JSON object. Do not include any text other than the JSON object.

    Conversation Transcript:
    {conversation}

    Based on the details in the conversation, construct a JSON object with the following fields:
    - "Name": "The full name of the individual involved."
    - "Email": "The email address provided."
    - "Phone Number": "The contact phone number."
    - "Location": "Specific location mentioned in relation to the issue."
    - "Department": "The department or agency mentioned."
    - "Issue": "Primary issue or concern raised."
    - "Service": "Specific service being discussed."
    - "Additional Information": "Any extra relevant details mentioned."
    - "Detailed Description": "A summary of the situation or problem as described."

    Ensure the output is a clean JSON object:
    {{
    "Name": "",
    "Email": "",
    "Phone Number": "",
    "Location": "",
    "Department": "",
    "Issue": "",
    "Service": "",
    "Additional Information": "",
    "Detailed Description": ""
    }}
"""

class LLMConfig:
    """ Encapsulates the AI model setup and interaction logic. """
    
    template = """
    As an AI expert assistant, your task is to analyze the provided conversation and directly extract and format specific information into a structured JSON object. Do not include any text other than the JSON object.

    Conversation Transcript:
    {conversation}

    Based on the details in the conversation, construct a JSON object with the following fields:
    - **Name**: The full name(s) of the individual(s) involved.
    - **Email**: The email address(es) cited.
    - **Phone Number**: Any phone number(s) provided.
    - **Location**: Details of any specific locations related to the issue or service.
    - **Department**: The department or entity involved, if mentioned.
    - **Issue**: A succinct description of the primary issue(s) discussed.
    - **Service**: The specific service(s) referenced in relation to the issue.
    - **Additional Information**: Other pertinent details or stakeholders mentioned.
    - **Detailed Description**: An in-depth summary of the concern or request, including desired outcomes, if any.

    Ensure the output is a clean JSON object:
    {{
    "Name": "",
    "Email": "",
    "Phone Number": "",
    "Location": "",
    "Department": "",
    "Issue": "",
    "Service": "",
    "Additional Information": "",
    "Detailed Description": ""
    }}
    
    """

    def __init__(self):
        """ Initialize the AI model with necessary parameters from the config. """
        self.llm = HuggingFaceTextGenInference(
            inference_server_url=config.inference_server_url,
            max_new_tokens=512,
            top_k=10,
            top_p=0.95,
            typical_p=0.95,
            temperature=0.1,
            repetition_penalty=1.175
        )
        self.llm_chain = LLMChain(prompt=PromptTemplate.from_template(template), llm=self.llm)

    def invoke(self, conversation):
        """ Invoke the LLMChain with a given conversation to process text. """
        return self.llm_chain.invoke({"conversation": conversation})

# The AIModel instance can be reused across different parts of the application.
llm_config = LLMConfig()

