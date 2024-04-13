# app.py
import argparse
import logging
from config.config_manager import config
from services.kafka_service import create_kafka_consumer, create_kafka_producer, send_message, receive_messages
from llms.llm_config import llm_config
from utilities.helpers import pretty_print_json, process_conversation

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the AI model in local or Kafka mode.")
    parser.add_argument("--local-mode", action="store_true", help="Run the application in local mode without Kafka.")
    parser.add_argument("--directory-path", type=str, default="data/conversations", help="Directory path for local mode data processing.")
    return parser.parse_args()

def handle_message(message):
    """Process messages received from Kafka."""
    response = llm_config.invoke(message.value['conversation'])
    pretty_print_json(response)  # For demonstration, print the processed result
    send_message(producer, config.producer_topic, response)

def run_kafka_mode():
    """Set up and process data using Kafka consumers and producers."""
    consumer = create_kafka_consumer(config.consumer_topic, "chat-group")
    producer = create_kafka_producer()

    receive_messages(consumer, handle_message)

def run_local_mode(directory_path):
    """Process all text files in the given directory as conversations."""
    from os import listdir
    from os.path import isfile, join

    files = [f for f in listdir(directory_path) if isfile(join(directory_path, f)) and f.endswith('.txt')]

    for file_name in files:
        file_path = join(directory_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            conversation_text = file.read().strip()
            if conversation_text:
                logging.info(f"Processing conversation from {conversation_text}")
                response = llm_config.invoke(conversation_text)
                text_content = response.get('text', '{}')
                print(text_content)
                pretty_print_json(process_conversation(text_content))  # Pretty print only the 'text' field

def main():
    args = parse_args()

    if args.local_mode:
        logging.info("Running in local mode.")
        run_local_mode(args.directory_path)
    else:
        logging.info("Running in Kafka mode.")
        run_kafka_mode()

if __name__ == "__main__":
    main()

# def convert_to_json(output):
#     """Converts structured text to JSON format."""
#     structured_text = output.get("text", "")
#     keys = ["Name", "Email", "Phone Number", "Department", "Issue", "Service", "Additional Information", "Detailed Description"]
#     data_dict = {}
#     for line in structured_text.split("\n"):
#         for key in keys:
#             if line.strip().startswith(f"- **{key}**"):
#                 value = line.split(f"- **{key}**:")[1].strip()
#                 if value.lower() in ["not available", "não disponível"]:
#                     value = None
#                 data_dict[key.replace(" ", "_").lower()] = value
#     return json.dumps(data_dict, indent=4, ensure_ascii=False)
