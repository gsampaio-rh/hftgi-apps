# Imports
from langchain.llms import HuggingFaceTextGenInference
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from kafka import KafkaConsumer, KafkaProducer
import json
import logging
import uuid
import os
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants for the HF Inference server setup
INFERENCE_SERVER_URL = os.getenv("INFERENCE_SERVER_URL", "http://localhost:3000/")

# Constants for the Kafka server setup
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")
CONSUMER_TOPIC = os.getenv("CONSUMER_TOPIC", "chat")
PRODUCER_TOPIC = os.getenv("PRODUCER_TOPIC", "answer")
CSV_FILE_PATH = "conversation_results.csv"

# Prompt Templates
template = """
        Analyze the provided conversation transcript to extract key information, presenting it in a structured and concise manner. Your task is to identify and parse out critical details such as personal names, email addresses, phone numbers, and any specific concerns or requests mentioned. The outcome should be a structured JSON output, containing the following fields:

        - **Name**: The full name(s) of the individual(s) involved.
        - **Email**: The email address(es) cited.
        - **Phone Number**: Any phone number(s) provided.
        - **Location**: Details of any specific locations related to the issue or service.
        - **Department**: The department or entity involved, if mentioned.
        - **Issue**: A succinct description of the primary issue(s) discussed.
        - **Service**: The specific service(s) referenced in relation to the issue.
        - **Additional Information**: Other pertinent details or stakeholders mentioned.
        - **Detailed Description**: An in-depth summary of the concern or request, including desired outcomes, if any.
        
        Expected Output Format:
        {{
        "Name": [...],
        "Email": [...],
        "Phone Number": [...],
        "Location": [...],
        "Department": [...],
        "Issue": [...],
        "Service": [...],
        "Additional Information": [...],
        "Detailed Description": [...]
        }}

        Ensure your response:
        - Adheres strictly to privacy and ethical guidelines, especially when handling personal information. Where direct extraction is not possible or could breach privacy, anonymize or generalize the data.
        - Is constructed in a clear, JSON-compatible format, avoiding assumptions not directly supported by the conversation data.
        - Preserves the original context and meaning of the conversation, summarizing repeated points once to maintain conciseness.

        In cases of ambiguous or inferred information, provide your best interpretation based on the context, noting any assumptions made.

        Conversation Transcript:
        {conversation}

        Note: Strive for clarity and brevity in your response, focusing on delivering a well-structured summary of the key conversation details.
        """

def save_to_csv(file_path, data_dict):
    """
    Saves a dictionary of conversation results to a CSV file, flattening any nested JSON structures.

    Parameters:
    - file_path (str): Path to the CSV file where the data will be saved.
    - data_dict (dict): Dictionary containing the conversation data to be saved.
    """
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        # Flatten the json_response dict into the main dict
        data_dict.update(data_dict.pop('json_response'))
        
        fieldnames = data_dict.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Check if the file is empty to write headers
        csvfile.seek(0, 2)  # Move to the end of the file
        if csvfile.tell() == 0:  # Check if file is empty
            writer.writeheader()  # Write headers if file is empty
        
        writer.writerow(data_dict)

# Kafka Consumer Setup
def create_kafka_consumer(server, topic, group_id):
    """Initializes and returns a Kafka Consumer."""
    return KafkaConsumer(
        topic,
        bootstrap_servers=[server],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

# Kafka Producer Setup
def create_kafka_producer(server):
    """Initializes and returns a Kafka Producer."""
    return KafkaProducer(
        bootstrap_servers=[server],
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    )

def convert_to_json(output):
    """Converts structured text to JSON format."""
    structured_text = output.get("text", "")
    keys = ["Name", "Email", "Phone Number", "Department", "Issue", "Service", "Additional Information", "Detailed Description"]
    data_dict = {}
    for line in structured_text.split("\n"):
        for key in keys:
            if line.strip().startswith(f"- **{key}**"):
                value = line.split(f"- **{key}**:")[1].strip()
                if value.lower() in ["not available", "não disponível"]:
                    value = None
                data_dict[key.replace(" ", "_").lower()] = value
    return json.dumps(data_dict, indent=4, ensure_ascii=False)

# Initialize LLMs and Chains
def setup_llm_chains(inference_url):
    """
    Initializes and configures the Large Language Model (LLM) Chains with the given inference server URL.
    
    This setup prepares an LLM for text generation by specifying behavior-modifying parameters to fine-tune
    the responses generated by the model. It encapsulates the model within an LLMChain, ready for executing
    text processing tasks using a predefined prompt template.
    
    Parameters:
    - inference_url (str): URL of the inference server where the LLM is hosted, responsible for performing
      the text generation tasks.
    
    Returns:
    - LLMChain: An instance of LLMChain, combining a prompt template with the LLM for text processing.
    
    The HuggingFaceTextGenInference model is initialized with the following parameters:
    - max_new_tokens (int): The maximum number of new tokens to generate. Set to 512, this limits the length
      of the generated response, controlling output verbosity.
    - top_k (int): Filters the generated predictions to the top-k probabilities before applying softmax.
      Set to 10, it focuses model choices, reducing the randomness of the response.
    - top_p (float): Nucleus sampling parameter controlling the cumulative probability cutoff. Set to 0.95,
      it allows for more diverse responses by only considering the top 95% probable options.
    - typical_p (float): Used to dynamically adjust top_p based on token probability distribution, aiming to
      maintain a typical set of options. Set to 0.95, it works in tandem with top_p for dynamic adjustments.
    - temperature (float): Controls the randomness of the output by scaling the logits before applying softmax.
      Set to 0.1, it produces more deterministic output, favoring higher probability options.
    - repetition_penalty (float): Increases/decreases the likelihood of previously generated tokens. Set to 1.175,
      it slightly penalizes repetition, encouraging more varied outputs.
    
    These parameters are carefully chosen to balance creativity, coherence, and control in the generated text,
    making the LLM more suitable for structured information extraction and analysis tasks.
    """
    qa_chain_prompt = PromptTemplate.from_template(template)
    
    llm = HuggingFaceTextGenInference(
        inference_server_url=inference_url,
        max_new_tokens=512,
        top_k=10,
        top_p=0.95,
        typical_p=0.95,
        temperature=0.1,
        repetition_penalty=1.175,
    )
    llm_chain = LLMChain(prompt=qa_chain_prompt, llm=llm)
    return llm_chain

def main():
    consumer = create_kafka_consumer(KAFKA_SERVER, CONSUMER_TOPIC, "chat-group")
    producer = create_kafka_producer(KAFKA_SERVER)
    llm_chain = setup_llm_chains(INFERENCE_SERVER_URL)

    for message in consumer:
        try:
            conversation_text = message.value['conversation']
            conversation_id = str(uuid.uuid4())
            logging.info(f"Processing conversation ID: {conversation_id}")
            logging.info(f"Chat: {conversation_text}")
            
            # Process the conversation
            response = llm_chain.invoke({"conversation": conversation_text})
            logging.info(f"LLM Response: {response}")
            
            # JSON
            json_response = convert_to_json(response)
            logging.info(f"JSON RESPONSE: {json_response}")

            # Prepare and send the response
            result = {
                "id": conversation_id,
                "conversation": conversation_text,
                "json_response": json.loads(json_response)
            }
            producer.send(PRODUCER_TOPIC, value=result)
            logging.info("Processed and sent conversation to 'answer' topic.")
            
            # Save the result to a CSV file
            save_to_csv(CSV_FILE_PATH, result)
            logging.info(f"Saved conversation ID: {conversation_id} to CSV file.")


        except Exception as e:
            logging.error(f"Error processing message: {e}", exc_info=True)

if __name__ == "__main__":
    main()