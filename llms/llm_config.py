# ai_model.py

from langchain.llms import HuggingFaceTextGenInference
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from config.config_manager import config

# - FALCON (spec: https://huggingface.co/tiiuae/falcon-7b/blob/main/tokenizer.json)
# Falcon special tokens include:
    # '>>TITLE<<', '>>ABSTRACT<<', '>>INTRODUCTION<<', '>>SUMMARY<<', '>>COMMENT<<',
    # '>>ANSWER<<', '>>QUESTION<<', '>>DOMAIN<<', '>>PREFIX<<', '>>SUFFIX<<', '>>MIDDLE<<',
    # along with various punctuation tokens.
    
# Use of >>INTRODUCTION<< to set the stage for the task
# Use of >>DOMAIN<< to introduce the conversation transcript
# Use of >>QUESTION<< to specify the details needed for the JSON object
# Use of >>ANSWER<< to clearly mark where the model’s output should begin

template = """
    >>INTRODUCTION<<
    As an AI expert assistant, analyze the provided conversation to directly extract specific information. Format this information into a structured JSON object following the guidelines below. Exclude any text that is not part of the JSON object.

    >>DOMAIN<<
    Conversation Transcript:
    {conversation}

    >>QUESTION<<
    Construct a JSON object based on the conversation details. Include the following fields:
    - **Name**: The full name(s) of the individual(s) involved.
    - **Email**: The email address(es) cited.
    - **Phone Number**: Any phone number(s) provided.
    - **Location**: Details of any specific locations related to the issue or service.
    - **Department**: The department or entity involved, if mentioned.
    - **Issue**: A succinct description of the primary issue(s) discussed.
    - **Service**: The specific service(s) referenced in relation to the issue.
    - **Additional Information**: Other pertinent details or stakeholders mentioned.
    - **Detailed Description**: An in-depth summary of the concern or request, including desired outcomes, if any.

    >>ANSWER<<
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

