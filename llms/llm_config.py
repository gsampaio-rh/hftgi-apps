# llm_config.py
from langchain_community.llms import HuggingFaceTextGenInference
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from config.config_manager import config
from config.instructions_templates import extraction_template, intent_classification_template

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
        # Initialize chains for each template
        self.extraction_chain = LLMChain(prompt=PromptTemplate.from_template(extraction_template), llm=self.llm)
        self.intent_classification_chain = LLMChain(prompt=PromptTemplate.from_template(intent_classification_template), llm=self.llm)

    def invoke(self, conversation, template_type='extraction'):
        """ Invoke the LLMChain with a given conversation to process text based on the specified template type. """
        if template_type == 'extraction':
            return self.extraction_chain.invoke({"conversation": conversation})
        elif template_type == 'intent_classification':
            return self.intent_classification_chain.invoke({"conversation": conversation})
        else:
            raise ValueError("Invalid template type specified")

# The LLMConfig instance can be reused across different parts of the application.
llm_config = LLMConfig()
