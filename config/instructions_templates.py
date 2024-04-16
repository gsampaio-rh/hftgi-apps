# instructions_templates.py

# - FALCON (spec: https://huggingface.co/tiiuae/falcon-7b/blob/main/tokenizer.json)
# Falcon special tokens include:
    # '>>TITLE<<', '>>ABSTRACT<<', '>>INTRODUCTION<<', '>>SUMMARY<<', '>>COMMENT<<',
    # '>>ANSWER<<', '>>QUESTION<<', '>>DOMAIN<<', '>>PREFIX<<', '>>SUFFIX<<', '>>MIDDLE<<',
    # along with various punctuation tokens.
    
# - '>>INTRODUCTION<<': Used to set the stage for the task, providing a contextual beginning to the input.
# - '>>DOMAIN<<': Introduces the conversation transcript, setting the domain-specific context for the model.
# - '>>QUESTION<<': Specifies the details required for constructing the JSON object, guiding the model on what information needs to be extracted.
# - '>>ANSWER<<': Clearly marks where the model’s output should begin, ensuring that the generated text is aligned with the expected response format.
# - '>>TITLE<<': Often used to indicate the beginning of a title in text generation tasks, guiding the model to format the following text accordingly.
# - '>>ABSTRACT<<': Used to start an abstract section, typically summarizing content, directing the model to generate a concise overview.
# - '>>SUMMARY<<': Signals the model to begin a summary, which could be of a longer text passage, aiming to condense information into essential points.
# - '>>COMMENT<<': Might be used to insert a comment or a remark within or about the text, possibly in a less formal or more conversational style.
# - '>>PREFIX<<', '>>SUFFIX<<', '>>MIDDLE<<': These tokens could be used to specify parts of the text where certain prefixes, suffixes, or middle sections are expected, possibly for tasks involving text editing or augmentation.
# - Punctuation tokens: Likely used to ensure proper punctuation in generated text, helping the model maintain grammatical standards.

extraction_template = """
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
        "name": "",
        "email": "",
        "phone_number": "",
        "location": "",
        "department": "",
        "issue": "",
        "service": "",
        "additional_information": "",
        "detailed_description": ""
    }}
    """

intent_classification_template = """
    >>INTRODUCTION<<
    As an AI expert assistant, you are tasked to analyze the provided conversation and classify the intent based on the dialogue. Identify the primary intent of the conversation from the list provided below and return only the most relevant category as a single line of text.

    >>DOMAIN<<
    Conversation Transcript:
    {conversation}

    >>QUESTION<<
    Which single category best describes the intent of the conversation? Choose one:
    - Accusation
    - Booking
    - Information Request
    - General Commentary
    - Complaint
    - Compliment

    >>ANSWER<<
    [Your single-category answer here without additional comments or explanations.]
    """

sentiment_extraction_template = """
    >>INTRODUCTION<<
    As an AI expert assistant, carefully analyze the sentiment of the provided conversation. Your task is to determine if the overall tone is positive, negative, or neutral.

    >>DOMAIN<<
    Conversation Transcript:
    {conversation}

    >>QUESTION<<
    What is the overall sentiment of the conversation? Provide your analysis based on the tone and content of the discussion.

    >>ANSWER<<
    The sentiment of the conversation is:
    [Positive, Negative, Neutral]
    """

summary_extraction_template = """
    >>INTRODUCTION<<
    As an AI, your task is to condense the provided conversation into a summary that could fit within a tweet. This summary should capture the key elements of the dialogue succinctly, like a highlight or a headline.

    >>DOMAIN<<
    Conversation Transcript:
    {conversation}

    >>QUESTION<<
    Produce a summary that encapsulates the core of the conversation in no more than 280 characters. This summary should be direct and to the point, effectively conveying the main issues or points discussed as if it were a tweet.

    >>ANSWER<<
    The tweet-like summary of the conversation is:
    [A concise, direct encapsulation, not exceeding 280 characters.]
    """